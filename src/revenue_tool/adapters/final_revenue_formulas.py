"""Excel rendering of the final-value contract (no LET/macros/helper sheets).

    All references stay in the same row, so sorting/column moves cannot couple
    a row to another contract. Python normalization remains authoritative for
    the full input grammar; unsupported live spellings ask for YYYY-MM.
"""
from revenue_tool.services.final_revenue import (
    FINAL_FIELD_SOURCES, YEAR_REQUIRED_HINT, INVALID_MONTH_HINT,
    INVALID_AMOUNT_HINT,
)


def _quote(text: str) -> str:
    return '"' + text.replace('"', '""') + '"'


def _trim(ref: str) -> str:
    return f'TRIM(CLEAN(SUBSTITUTE(SUBSTITUTE({ref},"　"," "),CHAR(160)," ")))'


def _blank(ref: str) -> str:
    text = f'LOWER({_trim(ref)})'
    checks = [f'{text}={_quote(v)}' for v in (
        "", "(空白)", "（空白）", "value", "#value", "#value!",
    )]
    return (f'IFERROR(OR(ISBLANK({ref}),AND(ISTEXT({ref}),OR({",".join(checks)}))),'
            f'IFERROR(ERROR.TYPE({ref})=3,FALSE))')


def _fallback(ref: str) -> str:
    return f'IF(ISBLANK({ref}),"",{ref})'


def _month_formula(manual: str, automatic: str, secondary: str) -> str:
    # The generated automatic months are canonical YYYY-MM or blank.
    ref = f'IF({automatic}<>"",{automatic},{secondary})'
    text = f'SUBSTITUTE({_trim(manual)}," ","")'
    digits = f'SUBSTITUTE(SUBSTITUTE({text},"月份",""),"月","")'
    month = f'VALUE({digits})'
    # Strict textual reconstruction rejects 9.5, 1e1, +9 and mixed suffixes.
    short = f'OR({text}=TEXT({month},"0"),{text}=TEXT({month},"00"),'
    short += f'{text}=TEXT({month},"0")&"月",{text}=TEXT({month},"00")&"月",'
    short += f'{text}=TEXT({month},"0")&"月份",{text}=TEXT({month},"00")&"月份")'
    diff = f'({month}-VALUE(RIGHT({ref},2)))'
    year = f'(VALUE(LEFT({ref},4))+IF({diff}>6,-1,IF({diff}<-6,1,0)))'
    nearest = (
        f'IF({ref}="",{_quote(YEAR_REQUIRED_HINT)},'
        f'IF(ABS({diff})=6,{_quote(YEAR_REQUIRED_HINT)},'
        f'IF(AND({year}>=1,{year}<=9999),'
        f'TEXT({year},"0000")&"-"&TEXT({month},"00"),'
        f'{_quote(INVALID_MONTH_HINT)})))'
    )
    # Explicit YYYY-M / YYYY-MM, independent of any automatic reference.
    yr = f'VALUE(LEFT({text},4))'
    mo = f'VALUE(MID({text},6,2))'
    full = (
        f'IF(AND({yr}>=1,{yr}<=9999,{mo}>=1,{mo}<=12,'
        f'OR({text}=TEXT({yr},"0000")&"-"&TEXT({mo},"0"),'
        f'{text}=TEXT({yr},"0000")&"-"&TEXT({mo},"00"))),'
        f'TEXT({yr},"0000")&"-"&TEXT({mo},"00"),'
        f'{_quote(INVALID_MONTH_HINT)})'
    )
    parsed = (
        f'IF(IFERROR(AND({month}>=1,{month}<=12,{short}),FALSE),'
        f'{nearest},{full})'
    )
    return (
        f'=IF({_blank(manual)},{_fallback(automatic)},'
        f'IFERROR({parsed},{_quote(INVALID_MONTH_HINT)}))'
    )


def final_formulas(refs: dict[str, str]) -> dict[str, str]:
    result = {}
    for final, (manual_field, auto_field) in FINAL_FIELD_SOURCES.items():
        manual, automatic = refs[manual_field], refs[auto_field]
        if final.startswith("final_revenue_month_"):
            other = "revenue_month_cpd" if final.endswith("rpd") else "revenue_month_rpd"
            result[final] = _month_formula(manual, automatic, refs[other])
        elif final == "final_revenue_forecast":
            amount = f'SUBSTITUTE({_trim(manual)},",","")'
            numeric = (f'IF(AND(LEFT({amount},1)="(",RIGHT({amount},1)=")"),'
                       f'-VALUE(MID({amount},2,LEN({amount})-2)),VALUE({amount}))')
            result[final] = (
                f'=IF({_blank(manual)},{_fallback(automatic)},'
                f'IFERROR(IF(ISLOGICAL({manual}),{_quote(INVALID_AMOUNT_HINT)},'
                f'ROUND({numeric},2)),{_quote(INVALID_AMOUNT_HINT)}))'
            )
        else:
            result[final] = f'=IF({_blank(manual)},{_fallback(automatic)},{manual})'
    return result
