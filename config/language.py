from typing import Any


LANGUAGE_OPTIONS = {
    "English": "en",
    "日本語": "ja",
}


TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # Application
        "app_name": "ESAA",
        "app_title": "Enterprise Security Audit Aggregator",
        "app_subtitle": (
            "Automated Windows and Linux security compliance "
            "assessment and enterprise reporting platform"
        ),
        "version": "Version",
        "development": "Development",
        "application": "Application",
        "supported_platforms": "Supported Platforms",
        "windows_server": "Windows Server",
        "linux_server": "Linux Server",
        "language": "Language",
        "workflow": "Workflow",
        "step_upload": "Upload audit ZIP",
        "step_discover": "Discover servers",
        "step_detect": "Detect operating systems",
        "step_evaluate": "Evaluate requirements",
        "step_review": "Review dashboard",
        "step_download": "Download Excel report",
        "clear_assessment": "Clear Current Assessment",

        # Upload
        "upload_title": "Upload Customer Audit Package",
        "upload_description": (
            "Upload a ZIP package containing security evidence "
            "collected from one or more Windows or Linux servers."
        ),
        "select_zip": "Select or drag and drop a ZIP file",
        "upload_help": (
            "The ZIP package may contain audit results from "
            "multiple servers."
        ),
        "upload_information": (
            "Upload a customer ZIP file to begin the assessment."
        ),
        "selected_file": "Selected File",
        "file_size": "File Size",
        "customer_name": "Customer or Project Name",
        "customer_placeholder": "Example: Contoso Security Assessment",
        "customer_help": (
            "Enter a customer, department or project name for "
            "this assessment."
        ),
        "run_assessment": "Run Security Assessment",
        "processing": "Analyzing the customer audit package...",
        "completed_successfully": (
            "Security assessment completed successfully."
        ),
        "servers_successfully_evaluated": (
            "{count} server(s) were successfully evaluated."
        ),

        # Errors
        "file_error": "File error",
        "invalid_input": "Invalid input",
        "assessment_error": "Assessment error",
        "unexpected_error": (
            "An unexpected error occurred while processing "
            "the audit package."
        ),
        "report_not_found": (
            "The assessment completed, but the generated "
            "Excel report was not found."
        ),
        "permission_error": (
            "The Excel report could not be created. Close any "
            "open report files and run the assessment again."
        ),
        "technical_details": "Technical details",

        # Tabs
        "tab_overview": "Overview",
        "tab_servers": "Servers",
        "tab_requirements": "Requirements",
        "tab_failures": "Failures",
        "tab_report": "Report",

        # Dashboard
        "compliance_score": "Compliance Score",
        "servers_evaluated": "Servers Evaluated",
        "requirements_evaluated": "Requirements Evaluated",
        "platform_summary": "Platform Summary",
        "windows_servers": "Windows Servers",
        "linux_servers": "Linux Servers",
        "unknown_platforms": "Unknown Platforms",
        "compliance_status": "Compliance Status",
        "status_distribution": "Requirement Status Distribution",
        "pass": "PASS",
        "fail": "FAIL",
        "manual": "MANUAL",
        "not_applicable": "N/A",
        "unknown": "UNKNOWN",
        "na_unknown": "N/A or Unknown",

        # Server inventory
        "server_inventory": "Server Inventory",
        "no_server_information": (
            "No server inventory information was found."
        ),
        "number": "No.",
        "hostname": "Hostname",
        "os_family": "OS Family",
        "operating_system": "Operating System",
        "ip_address": "IP Address",

        # Requirements
        "requirement_details": "Requirement Assessment Details",
        "no_requirement_details": (
            "No requirement details were found in the "
            "assessment results."
        ),
        "filter_server": "Filter by server",
        "filter_status": "Filter by status",
        "filter_os": "Filter by operating-system family",
        "filter_category": "Filter by category",
        "all_servers": "All servers",
        "all_statuses": "All statuses",
        "all_platforms": "All platforms",
        "all_categories": "All categories",
        "search_requirements": "Search requirement details",
        "search_placeholder": (
            "Search by requirement ID, name, value, evidence "
            "or recommendation"
        ),
        "displayed_requirements": "Displayed Requirements",
        "total_requirements": "Total Requirements",
        "no_filter_results": (
            "No requirements match the selected filters."
        ),
        "server": "Server",
        "requirement_id": "Requirement ID",
        "category": "Category",
        "requirement": "Requirement",
        "status": "Status",
        "expected_value": "Expected Value",
        "actual_value": "Actual Value",
        "evidence": "Evidence / Details",
        "recommendation": "Recommendation",

        # Failures
        "failed_requirements": "Failed Requirements",
        "no_failed_requirements": (
            "No failed automatic requirements were found."
        ),
        "failures_require_attention": (
            "{count} failed requirement(s) require review "
            "or remediation."
        ),

        # Report
        "assessment_report": "Assessment Report",
        "no_report": "No generated report is currently available.",
        "report_file": "Report file",
        "source_package": "Source package",
        "report_size": "Report size",
        "download_report": "Download Excel Report",
        "assessment_information": "Assessment Information",
        "customer_project": "Customer / Project",

        # Generic
        "unknown_value": "Unknown",
        "not_provided": "Not provided",
    },

    "ja": {
        # Application
        "app_name": "ESAA",
        "app_title": "企業向けセキュリティ監査集約システム",
        "app_subtitle": (
            "WindowsおよびLinuxサーバーのセキュリティ準拠状況を"
            "自動評価し、企業向けレポートを生成するプラットフォーム"
        ),
        "version": "バージョン",
        "development": "開発中",
        "application": "アプリケーション",
        "supported_platforms": "対応プラットフォーム",
        "windows_server": "Windows Server",
        "linux_server": "Linux Server",
        "language": "言語",
        "workflow": "処理フロー",
        "step_upload": "監査ZIPファイルをアップロード",
        "step_discover": "サーバーを検出",
        "step_detect": "OSを判定",
        "step_evaluate": "セキュリティ要件を評価",
        "step_review": "ダッシュボードを確認",
        "step_download": "Excelレポートをダウンロード",
        "clear_assessment": "現在の評価結果をクリア",

        # Upload
        "upload_title": "顧客監査パッケージのアップロード",
        "upload_description": (
            "1台以上のWindowsまたはLinuxサーバーから収集した"
            "セキュリティ証跡を含むZIPファイルをアップロードしてください。"
        ),
        "select_zip": "ZIPファイルを選択またはドラッグ＆ドロップ",
        "upload_help": (
            "ZIPファイルには複数サーバーの監査結果を含めることができます。"
        ),
        "upload_information": (
            "評価を開始するには、顧客監査ZIPファイルをアップロードしてください。"
        ),
        "selected_file": "選択されたファイル",
        "file_size": "ファイルサイズ",
        "customer_name": "顧客名またはプロジェクト名",
        "customer_placeholder": "例：Contoso セキュリティ評価",
        "customer_help": (
            "この評価に使用する顧客名、部署名、または"
            "プロジェクト名を入力してください。"
        ),
        "run_assessment": "セキュリティ評価を開始",
        "processing": "顧客監査パッケージを分析しています...",
        "completed_successfully": (
            "セキュリティ評価が正常に完了しました。"
        ),
        "servers_successfully_evaluated": (
            "{count}台のサーバーを正常に評価しました。"
        ),

        # Errors
        "file_error": "ファイルエラー",
        "invalid_input": "入力エラー",
        "assessment_error": "評価エラー",
        "unexpected_error": (
            "監査パッケージの処理中に予期しないエラーが発生しました。"
        ),
        "report_not_found": (
            "評価は完了しましたが、生成されたExcelレポートが"
            "見つかりませんでした。"
        ),
        "permission_error": (
            "Excelレポートを作成できませんでした。開いている"
            "レポートファイルを閉じて、もう一度実行してください。"
        ),
        "technical_details": "技術的な詳細",

        # Tabs
        "tab_overview": "概要",
        "tab_servers": "サーバー",
        "tab_requirements": "評価要件",
        "tab_failures": "不合格項目",
        "tab_report": "レポート",

        # Dashboard
        "compliance_score": "準拠スコア",
        "servers_evaluated": "評価済みサーバー",
        "requirements_evaluated": "評価済み要件",
        "platform_summary": "プラットフォーム概要",
        "windows_servers": "Windowsサーバー",
        "linux_servers": "Linuxサーバー",
        "unknown_platforms": "不明なプラットフォーム",
        "compliance_status": "準拠状況",
        "status_distribution": "評価結果の分布",
        "pass": "合格",
        "fail": "不合格",
        "manual": "手動確認",
        "not_applicable": "対象外",
        "unknown": "不明",
        "na_unknown": "対象外または不明",

        # Server inventory
        "server_inventory": "サーバー一覧",
        "no_server_information": (
            "サーバー情報が見つかりませんでした。"
        ),
        "number": "番号",
        "hostname": "ホスト名",
        "os_family": "OS種別",
        "operating_system": "オペレーティングシステム",
        "ip_address": "IPアドレス",

        # Requirements
        "requirement_details": "セキュリティ要件の評価詳細",
        "no_requirement_details": (
            "評価結果にセキュリティ要件の詳細が見つかりませんでした。"
        ),
        "filter_server": "サーバーで絞り込み",
        "filter_status": "ステータスで絞り込み",
        "filter_os": "OS種別で絞り込み",
        "filter_category": "カテゴリで絞り込み",
        "all_servers": "すべてのサーバー",
        "all_statuses": "すべてのステータス",
        "all_platforms": "すべてのプラットフォーム",
        "all_categories": "すべてのカテゴリ",
        "search_requirements": "評価結果を検索",
        "search_placeholder": (
            "要件ID、要件名、設定値、証跡、推奨事項を検索"
        ),
        "displayed_requirements": "表示中の要件数",
        "total_requirements": "要件総数",
        "no_filter_results": (
            "選択された条件に一致する要件はありません。"
        ),
        "server": "サーバー",
        "requirement_id": "要件ID",
        "category": "カテゴリ",
        "requirement": "セキュリティ要件",
        "status": "ステータス",
        "expected_value": "期待値",
        "actual_value": "実際の値",
        "evidence": "証跡・詳細",
        "recommendation": "推奨対応",

        # Failures
        "failed_requirements": "不合格となった要件",
        "no_failed_requirements": (
            "自動評価で不合格となった要件はありません。"
        ),
        "failures_require_attention": (
            "{count}件の不合格要件について確認または"
            "是正対応が必要です。"
        ),

        # Report
        "assessment_report": "評価レポート",
        "no_report": "現在ダウンロード可能なレポートはありません。",
        "report_file": "レポートファイル",
        "source_package": "元の監査パッケージ",
        "report_size": "レポートサイズ",
        "download_report": "Excelレポートをダウンロード",
        "assessment_information": "評価情報",
        "customer_project": "顧客・プロジェクト",

        # Generic
        "unknown_value": "不明",
        "not_provided": "未入力",
    },
}


def translate(
    key: str,
    language: str = "en",
    **values: Any,
) -> str:
    """
    Return translated text for the requested key.

    English is used as a fallback when a Japanese translation
    is unavailable.
    """

    selected_language = (
        language
        if language in TRANSLATIONS
        else "en"
    )

    text = TRANSLATIONS.get(
        selected_language,
        {},
    ).get(
        key,
        TRANSLATIONS["en"].get(key, key),
    )

    if not values:
        return text

    try:
        return text.format(**values)
    except (KeyError, IndexError, ValueError):
        return text