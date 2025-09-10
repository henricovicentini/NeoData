# app/utils/file_loader.py
import os
import zipfile
import tempfile
import pandas as pd


def load_dataframe(file_input):
    """
    Lê um arquivo e retorna um DataFrame pandas.
    Suporta: CSV, XLS, XLSX, JSON e ZIP contendo esses formatos.
    Também trata arquivos do tipo 'sociocsv' como CSV com separador ';'.
    """

    if hasattr(file_input, "filename"):
        fname = file_input.filename.lower()
    else:
        fname = str(file_input).lower()

    # ZIP
    if fname.endswith(".zip"):
        frames = []
        with tempfile.TemporaryDirectory() as tmpdir:
            if hasattr(file_input, "save"):
                path = os.path.join(tmpdir, file_input.filename)
                file_input.save(path)
            else:
                path = file_input

            with zipfile.ZipFile(path, "r") as z:
                namelist = z.namelist()
                for name in namelist:
                    lower_name = name.lower()
                    # Aceitar .csv ou extensões "sociocsv" como CSV
                    if lower_name.endswith(".csv") or lower_name.endswith("sociocsv"):
                        frames.append(pd.read_csv(z.open(name), sep=";", encoding="latin1", low_memory=False))
                    elif lower_name.endswith((".xls", ".xlsx")):
                        frames.append(pd.read_excel(z.open(name)))
                    elif lower_name.endswith(".json"):
                        frames.append(pd.read_json(z.open(name)))

        if not frames:
            raise ValueError(f"Nenhum arquivo legível encontrado no ZIP. Conteúdo: {namelist}")

        return pd.concat(frames, ignore_index=True)

    # CSV normal (ou .sociocsv)
    if fname.endswith(".csv") or fname.endswith("sociocsv"):
        return pd.read_csv(file_input, sep=";", encoding="latin1", low_memory=False)

    # Excel
    if fname.endswith((".xls", ".xlsx")):
        return pd.read_excel(file_input)

    # JSON
    if fname.endswith(".json"):
        return pd.read_json(file_input)

    raise ValueError("Formato de arquivo não suportado.")
