from pathlib import Path
import zipfile


def extract_zip(zip_path, output_folder):
    """
    Extract one ZIP file.

    Parameters
    ----------
    zip_path : str
        ZIP file path

    output_folder : str
        Folder where files will be extracted
    """

    zip_path = Path(zip_path)
    output_folder = Path(output_folder)

    output_folder.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(output_folder)

    print(f"Extracted: {zip_path.name}")