# app/utils/report_generator.py
import io
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet


def gerar_relatorio_pdf(doc_id, raw_df, clean_df, before, after, val):
    """
    Gera relatório PDF profissional com resumo, comparações e gráficos.
    """
    buffer = io.BytesIO()
    doc_pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    content = [Paragraph("Relatório de Limpeza de Dados - NeoData", styles["Title"]), Spacer(1, 12)]

    # ----------------- RESUMO -----------------
    summary = {
        "linhas_antes": int(raw_df.shape[0]) if not raw_df.empty else 0,
        "linhas_depois": int(clean_df.shape[0]),
        "colunas": int(clean_df.shape[1]),
        "ausentes_antes": int(raw_df.isna().sum().sum()) if not raw_df.empty else 0,
        "ausentes_depois": int(clean_df.isna().sum().sum()),
        "duplicadas_antes": int(raw_df.duplicated().sum()) if not raw_df.empty else 0,
        "duplicadas_depois": int(clean_df.duplicated().sum()),
    }

    if summary["linhas_antes"] > 0:
        content.append(Paragraph("Antes da Limpeza", styles["Heading2"]))
        content.append(Paragraph(
            f"O dataset tinha {summary['linhas_antes']} linhas e {before.get('shape', [0,0])[1]} colunas.",
            styles["Normal"]
        ))
        if summary["ausentes_antes"] > 0:
            content.append(Paragraph(f"Havia {summary['ausentes_antes']} valores ausentes.", styles["Normal"]))
        if summary["duplicadas_antes"] > 0:
            content.append(Paragraph(f"Foram encontrados {summary['duplicadas_antes']} registros duplicados.", styles["Normal"]))

    if summary["linhas_depois"] > 0:
        content.append(Spacer(1, 12))
        content.append(Paragraph("Depois da Limpeza", styles["Heading2"]))
        content.append(Paragraph(
            f"O dataset passou a ter {summary['linhas_depois']} linhas e {summary['colunas']} colunas.",
            styles["Normal"]
        ))
        if summary["ausentes_depois"] > 0:
            content.append(Paragraph(f"Ainda restam {summary['ausentes_depois']} valores ausentes.", styles["Normal"]))
        else:
            content.append(Paragraph("Não restaram valores ausentes.", styles["Normal"]))
        if summary["duplicadas_depois"] == 0:
            content.append(Paragraph("Nenhum registro duplicado permaneceu.", styles["Normal"]))

    # ----------------- VALIDAÇÃO -----------------
    if val:
        content.append(Spacer(1, 12))
        content.append(Paragraph("Validação", styles["Heading2"]))
        if val.get("valid", False):
            content.append(Paragraph("Os dados finais passaram em todas as validações principais.", styles["Normal"]))
        else:
            messages = val.get("messages", None)
            if messages:
                content.append(Paragraph("Foram encontradas inconsistências:", styles["Normal"]))
                for m in messages if isinstance(messages, (list, tuple)) else [messages]:
                    content.append(Paragraph(f"- {m}", styles["Normal"]))

    # ----------------- COMPARAÇÕES VISUAIS -----------------
    numeric_cols = list(
        set(raw_df.select_dtypes(include="number").columns) &
        set(clean_df.select_dtypes(include="number").columns)
    )[:3]

    for col in numeric_cols:
        fig, axes = plt.subplots(1, 2, figsize=(8, 3))

        # Antes
        if col in raw_df.columns and not raw_df[col].dropna().empty:
            raw_df[col].dropna().hist(bins=20, ax=axes[0], color="red", alpha=0.7)
            axes[0].set_title(f"Antes - {col}")
        else:
            axes[0].text(0.5, 0.5, "Não disponível", ha="center", va="center")

        # Depois
        if not clean_df[col].dropna().empty:
            clean_df[col].dropna().hist(bins=20, ax=axes[1], color="green", alpha=0.7)
            axes[1].set_title(f"Depois - {col}")
        else:
            axes[1].text(0.5, 0.5, "Sem dados", ha="center", va="center")

        fig.suptitle(f"Distribuição - {col}", fontsize=12)
        plt.tight_layout()

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format="png")
        plt.close()
        img_buf.seek(0)

        content.append(Paragraph(f"Comparação Antes vs Depois da coluna {col}", styles["Heading3"]))
        content.append(Image(img_buf, width=400, height=200))
        content.append(Spacer(1, 12))

    # ----------------- BUILD -----------------
    doc_pdf.build(content)
    buffer.seek(0)
    return buffer
