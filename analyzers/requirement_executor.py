from analyzers.compliance_engine import evaluate
from parsers.parser_factory import get_parser


def execute_requirement(server_folder, config):
    """
    Execute one requirement.

    The parser receives:
        - server_folder
        - requirement workflow configuration

    This allows the parser to read the files listed in windows.json.
    """

    parser_name = config.get("parser")

    parser = get_parser(parser_name)

    if parser is None:
        return {
            "status": "NOT_IMPLEMENTED"
        }

    parsed_data = parser(
        server_folder,
        config
    )

    result = evaluate(
        parsed_data,
        config["requirement"]
    )

    return result