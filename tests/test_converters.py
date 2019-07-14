from analyst.converters import LowerCaseAlphaNumConverter, IPV4Converter


def test_lowercasealphanumconverter_good():
    value = "NotAlphaNum 123!"
    converter = LowerCaseAlphaNumConverter()
    assert converter.convert(value) is None


def test_lowercasealphanumconverter_bad():
    value = "IsAlphaNum-123"
    converter = LowerCaseAlphaNumConverter()
    assert converter.convert(value) == "isalphanum-123"


def test_ipv4converter_bad():
    value = "notAIP1234"
    converter = IPV4Converter()
    assert converter.convert(value) is None


def test_ipv4converter_god():
    value = "1.1.1.1"
    converter = IPV4Converter()
    assert converter.convert(value) == value
