"""Image Processing Studio — four course sections, nine algorithm groups."""
from __future__ import annotations

from html import escape
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import cv2
import numpy as np
import streamlit as st

from processing import (
    Recommendation, arithmetic, brightness_stats, custom_grayscale,
    decode_image, denoise, edge_detection, eliminate_channels, encode_png,
    histogram_enhancement, psnr, recommendation_for, rgb_channels,
    sharpening, snr, solarization,
)
from ui_style import theme_css

st.set_page_config(page_title="Image Processing Studio", page_icon=":material/image_search:",
                   layout="wide", initial_sidebar_state="expanded")

ROOT = Path(__file__).resolve().parent
SAMPLE_DIR = ROOT / "assets" / "samples"
SECTIONS = {
    "Color Fundamentals": ("RGB Separation", "Custom Grayscale"),
    "Point Operations": ("Arithmetic", "Complementary / Solarization", "Channel Elimination"),
    "Contrast & Histogram": ("Histogram Enhancement",),
    "Filters & Edges": ("Noise Reduction", "Sharpening", "Edge Detection"),
}
SECTION_ICONS = (":material/palette:", ":material/tune:", ":material/contrast:", ":material/filter_alt:")
NAV_KEYS = ("nav_colors", "nav_points", "nav_contrast", "nav_filters")
SAMPLES = {
    "RGB Separation": "01_T1_RGB_Separation_Coffee.png",
    "Custom Grayscale": "02_T1_Grayscale_Astronaut.png",
    "Arithmetic": "03_T2_Arithmetic_Dark_Astronaut.png",
    "Complementary / Solarization": "04_T2_Solarization_Rocket.jpg",
    "Channel Elimination": "05_T2_Channel_Elimination_Blue_Cast.png",
    "Histogram Enhancement": "06_T3_Histogram_Low_Contrast_Astronaut.png",
    "Noise Reduction": "07_T4_Noise_Reduction_Clean_Coffee.png",
    "Sharpening": "08_T4_Sharpening_Cat.png",
    "Edge Detection": "09_T4_Edge_Detection_Coffee.png",
}
DETAILS = {
    "RGB Separation": "Explore the red, green, and blue intensity maps and isolated color channels.",
    "Custom Grayscale": "Convert color to grayscale with the notebook's weighted RGB formula.",
    "Arithmetic": "Apply one brightness operation, or compare all four using a declared exposure goal.",
    "Complementary / Solarization": "Explore full color inversion and selective inversion above a threshold.",
    "Channel Elimination": "Remove one RGB channel; compare channel statistics before choosing.",
    "Histogram Enhancement": "Contrast stretching vs equalization, with optional brightness offset.",
    "Noise Reduction": "Add salt-and-pepper noise and compare three smoothers against a clean reference.",
    "Sharpening": "Blur a clean image, then reconstruct it with a custom sharpening kernel.",
    "Edge Detection": "Grayscale → Gaussian pre-blur → Canny contours.",
}
BUTTON_ICONS = {
    "Addition (+)": ":material/add:", "Subtraction (-)": ":material/remove:",
    "Multiplication (*)": ":material/close:", "Division (/)": ":material/percent:",
    "Complementary": ":material/invert_colors:", "Solarization": ":material/brightness_high:",
    "Remove Red": ":material/filter_1:", "Remove Green": ":material/filter_2:",
    "Remove Blue": ":material/filter_3:",
    "Stretching": ":material/open_in_full:", "Equalization": ":material/equalizer:",
    "Average Filter": ":material/blur_on:", "Gaussian Filter": ":material/blur_on:",
    "Median Filter": ":material/filter_center_focus:",
    "Canny Edges": ":material/gesture:", "Custom Sharpening": ":material/auto_fix_high:",
}


def set_section(name: str) -> None:
    st.session_state["section"] = name


def set_active_choice(module: str, choice: str) -> None:
    st.session_state[f"choice::{module}"] = choice


def switch_theme() -> None:
    st.session_state["dark_mode"] = not st.session_state.get("dark_mode", True)


def compute(module: str, img: np.ndarray, params: dict) -> dict[str, np.ndarray]:
    if module == "RGB Separation":
        return rgb_channels(img)
    if module == "Custom Grayscale":
        return {"Custom Grayscale": custom_grayscale(img)}
    if module == "Arithmetic":
        return arithmetic(img, params["amount"], params["factor"])
    if module == "Complementary / Solarization":
        return solarization(img, params["threshold"])
    if module == "Channel Elimination":
        return eliminate_channels(img)
    if module == "Histogram Enhancement":
        return histogram_enhancement(img, params["brightness"])
    if module == "Noise Reduction":
        return denoise(img, params["density"] / 100, params["kernel"], params["seed"])
    if module == "Sharpening":
        return sharpening(img, params["blur_kernel"])
    if module == "Edge Detection":
        return edge_detection(img, params["low"], params["high"])
    raise ValueError(f"Unknown group: {module}")


def settings_for(module: str) -> dict:
    values: dict = {}
    with st.sidebar:
        st.markdown('<div class="ip-mini-title">Fine-tune</div>', unsafe_allow_html=True)
        if module == "Arithmetic":
            values["amount"] = st.slider("Amount for + / −", 0, 100, 40, key="amount")
            values["factor"] = st.slider("Factor for × / ÷", 1.05, 3.0, 1.3, 0.05, key="factor")
            values["exposure_goal"] = st.selectbox("Recommendation goal", ["Auto", "Brighten", "Darken"],
                                                     help="Auto uses original median below 90 for brighten, above 175 for darken; otherwise no automatic winner.")
        elif module == "Complementary / Solarization":
            values["threshold"] = st.slider("Solarization threshold", 0, 255, 128)
            values["effect_goal"] = st.selectbox("Visual goal", ["Selective highlight inversion", "Full color inversion"])
        elif module == "Histogram Enhancement":
            values["brightness"] = st.slider("Additional brightness", -80, 80, 0)
        elif module == "Noise Reduction":
            values["density"] = st.slider("Noise density (%)", 0, 35, 5)
            values["kernel"] = st.select_slider("Filter kernel", [3, 5, 7], value=3)
            values["seed"] = st.number_input("Random seed", min_value=0, max_value=10000, value=7)
        elif module == "Sharpening":
            values["blur_kernel"] = st.select_slider("Blur kernel", [3, 5, 7, 9], value=7)
        elif module == "Edge Detection":
            values["low"] = st.slider("Canny lower threshold", 0, 200, 50)
            values["high"] = st.slider("Canny upper threshold", values["low"]+1, 255,
                                       max(150, values["low"]+1))
        else:
            st.caption("No parameters for this algorithm group.")
    return values


def choose_result(module: str, names: list[str]) -> str:
    key = f"choice::{module}"
    valid = [*names, "Compare All"]
    if st.session_state.get(key) not in valid:
        st.session_state[key] = names[0]
    st.markdown('<div class="ip-mini-title">Try one operation</div>', unsafe_allow_html=True)
    for idx in range(0, len(names), 4):
        block = names[idx:idx+4]
        cols = st.columns(len(block), gap="small")
        for col, name in zip(cols, block):
            with col:
                st.button(name, icon=BUTTON_ICONS.get(name),
                          key=f"single::{module}::{name}",
                          type="primary" if st.session_state[key] == name else "secondary",
                          use_container_width=True, on_click=set_active_choice,
                          args=(module, name))
    st.button("Compare all  ·  Recommendation", icon=":material/grid_view:",
              key="compare_all_button", use_container_width=True,
              type="primary" if st.session_state[key] == "Compare All" else "secondary",
              on_click=set_active_choice, args=(module, "Compare All"))
    return st.session_state[key]


def get_input_image(module: str) -> tuple[np.ndarray | None, str]:
    with st.container(border=True):
        col_up, col_sample = st.columns([1.65, 1], gap="large")
        with col_up:
            uploaded = st.file_uploader("Upload your image", type=["png", "jpg", "jpeg"],
                                        key="uploaded_image",
                                        help="A single uploaded image is used across all algorithm groups.")
        with col_sample:
            sample_name = st.selectbox("Or pick a sample", options=list(SAMPLES),
                                       index=list(SAMPLES).index(module),
                                       key=f"sample::{module}")
            st.caption("Upload takes priority. Remove it to use a sample.")
    try:
        if uploaded is not None:
            return decode_image(uploaded.getvalue()), f"Uploaded · {uploaded.name}"
        f = SAMPLE_DIR / SAMPLES[sample_name]
        if not f.is_file():
            st.error("Demo image missing. Upload your own JPG or PNG.")
            return None, "Missing image"
        return decode_image(f.read_bytes()), f"Demo · {sample_name}"
    except ValueError as exc:
        st.error(str(exc))
        return None, "Invalid image"


def result_zip(original: np.ndarray, results: dict[str, np.ndarray]) -> bytes:
    buf = BytesIO()
    with ZipFile(buf, "w", ZIP_DEFLATED) as zf:
        zf.writestr("00_Original.png", encode_png(original))
        for idx, (label, result) in enumerate(results.items(), start=1):
            filename = "".join(ch if ch.isalnum() else "_" for ch in label).strip("_")
            zf.writestr(f"{idx:02d}_{filename}.png", encode_png(result))
    return buf.getvalue()


def show_table(records: list[dict] | tuple[dict, ...]) -> None:
    """Small semantic comparison table, palette-controlled in both themes."""
    if not records:
        return
    headers=list(records[0])
    header_html="".join(f"<th scope='col'>{escape(str(name))}</th>" for name in headers)
    rows_html="".join(
        "<tr>" + "".join(f"<td>{escape(str(record.get(name, '')))}</td>" for name in headers) + "</tr>"
        for record in records
    )
    st.markdown(f'<div class="ip-table-wrap"><table class="ip-data-table">'
                f'<thead><tr>{header_html}</tr></thead><tbody>{rows_html}</tbody></table></div>',
                unsafe_allow_html=True)


def show_histogram(outputs: dict[str, np.ndarray], active: str) -> None:
    """Render a theme-consistent vector plot of actual 256-bin histograms."""
    targets=["Grayscale (before)"]
    if active == "Compare All":
        targets.extend(["Stretching", "Equalization"])
    elif active != "Grayscale (before)":
        targets.append(active)
    hists={key: np.bincount(outputs[key].ravel(),minlength=256) for key in targets}
    peak=max(int(v.max()) for v in hists.values())
    if peak == 0:
        return
    dark=st.session_state.get("dark_mode", True)
    colors=["#87B6FF", "#47D5B5", "#F4C27B"] if dark else ["#285CC2", "#078673", "#9A6513"]
    left,right,top,bottom=45,760,15,188
    width=right-left
    height=bottom-top
    lines=[]
    for label,color in zip(targets,colors):
        counts=hists[label]
        points=" ".join(f"{left+width*i/255:.1f},{bottom-height*int(v)/peak:.1f}" for i,v in enumerate(counts))
        lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.2" points="{points}"/>')
    grid=[]
    for x in (0,64,128,192,255):
        xpos=left+width*x/255
        grid.append(f'<line x1="{xpos:.1f}" y1="{top}" x2="{xpos:.1f}" y2="{bottom}" stroke="var(--ip-border)"/>')
        grid.append(f'<text x="{xpos:.1f}" y="207" text-anchor="middle" fill="var(--ip-muted)" font-size="12">{x}</text>')
    for frac in (0,.5,1):
        ypos=bottom-height*frac
        grid.append(f'<line x1="{left}" y1="{ypos:.1f}" x2="{right}" y2="{ypos:.1f}" stroke="var(--ip-border)"/>')
    legend="".join(f'<span class="ip-chart-dot" style="background:{color}"></span>{escape(label)}' for label,color in zip(targets,colors))
    st.markdown("#### Intensity histogram")
    aria_label = escape(", ".join(targets))
    st.markdown(f'<svg class="ip-histogram" viewBox="0 0 790 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Intensity histograms for: {aria_label}">'
                +"".join(grid)+"".join(lines)+'</svg><div class="ip-chart-legend">'
                +legend+'</div>',unsafe_allow_html=True)


def analysis_panel(module: str, img: np.ndarray, outputs: dict[str, np.ndarray], active: str, params: dict) -> None:
    with st.expander("Measurements & processing details", expanded=(active == "Compare All")):
        if module == "Channel Elimination":
            channel_means = img.mean(axis=(0, 1))
            a,b,c = st.columns(3)
            a.metric("Mean Red", f"{channel_means[0]:.1f}")
            b.metric("Mean Green", f"{channel_means[1]:.1f}")
            c.metric("Mean Blue", f"{channel_means[2]:.1f}")
            st.markdown("**First 3 × 3 RGB matrix**")
            st.code(np.array2string(img[:3, :3, :]), language="text")
        elif module == "Arithmetic":
            stats=brightness_stats(img)
            a,b,c=st.columns(3)
            a.metric("Original mean", f"{stats['mean']:.1f}")
            b.metric("Original contrast", f"{stats['contrast']:.1f}")
            c.metric("Original near-white", f"{stats['white_pct']:.2f}%")
        elif module == "Histogram Enhancement":
            show_histogram(outputs, active)
        elif module == "Noise Reduction":
            scores=[{"Stage":label, "SNR (dB)":round(snr(img, result),2)} for label,result in outputs.items()]
            show_table(scores)
            st.caption("The original image is a known clean reference before salt-and-pepper noise is injected.")
        elif module == "Sharpening":
            scores=[{"Stage":label, "PSNR to clean original (dB)":round(psnr(img, result),2)} for label,result in outputs.items()]
            show_table(scores)
        elif module == "Edge Detection":
            edge_pct=100*np.count_nonzero(outputs["Canny Edges"])/outputs["Canny Edges"].size
            st.metric("Edge pixels",f"{edge_pct:.2f}%")
        elif module == "RGB Separation":
            means=img.mean(axis=(0,1))
            st.write(f"R: **{means[0]:.1f}** · G: **{means[1]:.1f}** · B: **{means[2]:.1f}**")
        elif module == "Custom Grayscale":
            st.code("Gray = 0.299 * R + 0.587 * G + 0.114 * B", language="python")
        elif module == "Complementary / Solarization":
            fraction = 100*float(np.mean(img > params["threshold"]))
            st.write(f"Threshold: **{params['threshold']}** · Channel values above threshold: **{fraction:.2f}%**")


def recommendation_panel(rec: Recommendation) -> None:
    name = rec.operation
    header = f"Recommended · {name}" if name else "No defensible automatic winner"
    mode = "" if name else " no-winner"
    evidence = "".join(f'<span class="ip-evidence">{escape(item)}</span>' for item in rec.evidence)
    goal = f'<div class="ip-mini-title">Goal · {escape(rec.goal)}</div>' if rec.goal else ""
    st.markdown(
        f'<div class="ip-decision{mode}">{goal}'
        f'<div class="ip-decision-title">{escape(header)}</div>'
        f'<div class="ip-decision-desc">{escape(rec.reason)}</div>'
        f'{evidence}</div>', unsafe_allow_html=True,
    )
    st.caption(f"**Decision rule:** {rec.basis}")
    if rec.rows:
        st.markdown("**Measured comparison**")
        show_table(rec.rows)
    if rec.limitation:
        st.caption(f"**What this does NOT prove:** {rec.limitation}")


def main() -> None:
    st.session_state.setdefault("dark_mode", True)
    st.session_state.setdefault("section", next(iter(SECTIONS)))
    # CSS must be installed before body widgets to avoid split-looking light mode.
    st.markdown(theme_css(st.session_state["dark_mode"]), unsafe_allow_html=True)

    hero, toggle=st.columns([12,1],gap="small", vertical_alignment="center")
    with hero:
        st.markdown('<p class="ip-eyebrow">Interactive OpenCV workshop</p>'
                    '<h1 class="ip-headline">Image Processing Studio</h1>'
                    '<p class="ip-muted">One image. Nine techniques. Explore each result or compare the methods side by side.</p>',
                    unsafe_allow_html=True)
    with toggle:
        st.button("Toggle theme", icon=":material/light_mode:" if st.session_state["dark_mode"] else ":material/dark_mode:",
                  key="theme_toggle", help="Switch between light and dark appearance", on_click=switch_theme)

    st.markdown('<div class="ip-mini-title">Explore a category</div>', unsafe_allow_html=True)
    sections=list(SECTIONS)
    columns=st.columns(4,gap="small")
    for col,section,icon,key in zip(columns,sections,SECTION_ICONS,NAV_KEYS):
        with col:
            st.button(section, key=key, icon=icon,
                      type="primary" if st.session_state["section"]==section else "secondary",
                      use_container_width=True, on_click=set_section, args=(section,))
    section=st.session_state["section"]
    with st.sidebar:
        st.markdown('<p class="ip-eyebrow">Processing workspace</p>', unsafe_allow_html=True)
        st.markdown('### Choose a technique')
        module=st.radio("Technique", SECTIONS[section], key=f"module::{section}", label_visibility="collapsed")
        st.divider()
    params=settings_for(module)
    with st.sidebar:
        st.divider()
        st.caption("OpenCV · NumPy · Nine practical modules")
        st.caption("Selection rules are educational and explain their limits.")

    st.markdown(f'<span class="ip-chip">{escape(section)}</span>'
                f'<span class="ip-chip">{SECTIONS[section].index(module)+1} of {len(SECTIONS[section])} techniques</span>', unsafe_allow_html=True)
    st.subheader(module)
    st.caption(DETAILS[module])
    img,source=get_input_image(module)
    if img is None:
        st.stop()
    st.caption(f"{source} · {img.shape[1]} × {img.shape[0]} px")
    try:
        outputs=compute(module,img,params)
    except (ValueError,cv2.error) as exc:
        st.error(f"Could not process the selected image: {exc}")
        st.stop()

    active=choose_result(module,list(outputs))
    st.markdown('<div class="ip-mini-title">Live preview</div>', unsafe_allow_html=True)
    left,right=st.columns([1,1.8],gap="large")
    with left:
        st.markdown("#### Original")
        with st.container(border=True):
            st.image(img,use_container_width=True)
            st.caption("Unchanged source · always visible")
            st.download_button("Save original",encode_png(img),file_name="Original.png",mime="image/png",
                               icon=":material/download:",use_container_width=True,key="save_original")
    with right:
        if active != "Compare All":
            st.markdown(f"#### {active}")
            with st.container(border=True):
                result=outputs[active]
                st.image(result,use_container_width=True)
                st.caption(f"Individual preview · {active}")
                filename="".join(ch if ch.isalnum() else "_" for ch in active).strip("_")
                st.download_button("Save result", encode_png(result), file_name=f"{filename}.png",
                                   mime="image/png",icon=":material/download:",use_container_width=True,
                                   key=f"save::{module}::{active}")
        else:
            st.markdown("#### Full comparison")
            rec=recommendation_for(module,img,outputs,**params)
            names=list(outputs)
            for idx in range(0,len(names),2):
                pair=names[idx:idx+2]
                cards=st.columns(len(pair),gap="small")
                for card,name in zip(cards,pair):
                    with card:
                        with st.container(border=True):
                            status=" · **Suggested**" if rec.operation==name else ""
                            st.markdown(f"**{name}**{status}")
                            st.image(outputs[name],use_container_width=True)
            st.download_button("Save all results · ZIP",result_zip(img,outputs),
                               file_name="Image_Processing_Comparison.zip",mime="application/zip",
                               icon=":material/archive:",use_container_width=True,key=f"save_all::{module}")
    if active == "Compare All":
        st.markdown("### Selection & evidence")
        recommendation_panel(rec)
    analysis_panel(module,img,outputs,active,params)
    st.markdown('<div class="ip-footer">Image Processing Studio · Lab project · Method rankings are scoped to the measured goal; no universal visual-quality winner is implied.</div>',unsafe_allow_html=True)


if __name__=="__main__":
    main()
