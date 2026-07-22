from parsers.log_retention_parser import parse_log_retention


def test_log_retention_parser():
    sample_content = """
name: Security
enabled: true
type: Admin
owningPublisher:
isolation: Custom
channelAccess: O:BAG:SYD:(A;;0xf0005;;;SY)
logging:
  logFileName: %SystemRoot%\\System32\\Winevt\\Logs\\Security.evtx
  retention: false
  autoBackup: false
  maxSize: 20971520
publishing:
  fileMax: 1
"""

    result = parse_log_retention(sample_content)

    print(result)

    assert result["LOG_ENABLED"] is True
    assert result["RETENTION"] is False
    assert result["AUTO_BACKUP"] is False

    assert result["MAX_SIZE_BYTES"] == 20971520
    assert result["MAX_SIZE_MB"] == 20.0
    assert result["MAX_SIZE_CONFIGURED"] is True

    print("Log retention parser test passed.")


if __name__ == "__main__":
    test_log_retention_parser()