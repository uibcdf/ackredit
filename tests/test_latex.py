from ackredit import register_item, report, track_item


def test_latex_generation():
    register_item(
        id="molsysmt:2024",
        type="article",
        title="MolSysMT Paper & Stuff",
        authors=["Diego", "Other Author"],
        year=2024,
    )
    track_item("molsysmt:2024", used_by="main_script")

    tex_str = report(format="latex")

    # Check structure
    assert "\\documentclass" in tex_str
    assert "\\begin{document}" in tex_str
    assert "\\end{document}" in tex_str
    assert "\\bibliographystyle{plainnat}" in tex_str
    assert "\\bibliography{ackredit_report}" in tex_str

    # Check item rendering (with escaped chars)
    assert "\\textbf{MolSysMT Paper \\& Stuff}" in tex_str
    assert "\\citep{molsysmt-2024}" in tex_str
    assert "\\textit{(Used via: main\\_script)}" in tex_str
