from utils.config_loader import load_json


def normalize(parsed_data, mapping_file):
    """
    Generic normalizer.

    Parameters
    ----------
    parsed_data : dict
        Output from a parser.

    mapping_file : str
        JSON mapping file.

    Returns
    -------
    dict
        Normalized data.
    """

    mapping = load_json(mapping_file)

    normalized = {}

    for internal_key, config in mapping.items():

        aliases = config["aliases"]

        for original_name, value in parsed_data.items():

            if original_name in aliases:

                normalized[internal_key] = value

    return normalized