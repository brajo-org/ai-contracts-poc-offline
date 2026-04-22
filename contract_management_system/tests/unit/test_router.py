from app.core.router import route_document


def test_route_document():
    assert route_document("pdf") == "pdf"
    assert route_document("docx") == "docx"
    assert route_document("xlsx") == "excel"
    assert route_document("exe") == "reject"
