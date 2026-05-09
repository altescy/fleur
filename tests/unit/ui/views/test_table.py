from fleur import emit
from fleur.ui import Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow


class TestTable:
    def test_table_views_compile_semantic_tags_and_defaults(self) -> None:
        source = emit(
            Table(
                TableHeader(
                    TableRow(
                        TableHead("Name"),
                        TableHead("Role", align="right"),
                    )
                ),
                TableBody(
                    TableRow(
                        TableCell("Alice"),
                        TableCell("Admin", align="right"),
                    )
                ),
                TableCaption("Team members"),
            ).__compile__()
        )

        assert '__fleur.h("table"' in source
        assert '__fleur.h("thead"' in source
        assert '__fleur.h("tbody"' in source
        assert '__fleur.h("tr"' in source
        assert '__fleur.h("th"' in source
        assert '__fleur.h("td"' in source
        assert '__fleur.h("caption"' in source
        assert '"border-bottom": "1px solid var(--fleur-color-border-default)"' in source
        assert '"text-align": "right"' in source
