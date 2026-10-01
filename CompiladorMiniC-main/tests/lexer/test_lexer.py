"""Pruebas del analizador léxico de Mini C (Taller N°6 UTP-FISC)."""

import pytest

from minic.diagnostics.diagnostic import Diagnostic
from minic.lexer.lexer import Lexer
from minic.lexer.token import Token
from minic.lexer.token_type import TokenType
from minic.output.diagnostic_printer import format_diagnostic
from minic.output.token_printer import format_token


def test_section7_case1_valid_source() -> None:
    source = "int2 = 12abc;\nwhilex == -5"
    result = Lexer(source).scan()

    assert result.diagnostics == []
    assert len(result.tokens) == 10

    expected = [
        Token(TokenType.IDENTIFIER, "int2", None, 1, 1),
        Token(TokenType.ASSIGN, "=", None, 1, 6),
        Token(TokenType.INTEGER_LITERAL, "12", 12, 1, 8),
        Token(TokenType.IDENTIFIER, "abc", None, 1, 10),
        Token(TokenType.SEMICOLON, ";", None, 1, 13),
        Token(TokenType.IDENTIFIER, "whilex", None, 2, 1),
        Token(TokenType.EQUAL_EQUAL, "==", None, 2, 8),
        Token(TokenType.MINUS, "-", None, 2, 11),
        Token(TokenType.INTEGER_LITERAL, "5", 5, 2, 12),
        Token(TokenType.EOF, "", None, 2, 13),
    ]
    assert result.tokens == expected

    formatted = [format_token(t) for t in result.tokens]
    assert formatted == [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]


def test_section7_case2_source_with_errors() -> None:
    source = "int x = @;\nx ! = 0; // fin"
    result = Lexer(source).scan()

    expected_tokens = [
        Token(TokenType.KW_INT, "int", None, 1, 1),
        Token(TokenType.IDENTIFIER, "x", None, 1, 5),
        Token(TokenType.ASSIGN, "=", None, 1, 7),
        Token(TokenType.SEMICOLON, ";", None, 1, 10),
        Token(TokenType.IDENTIFIER, "x", None, 2, 1),
        Token(TokenType.ASSIGN, "=", None, 2, 5),
        Token(TokenType.INTEGER_LITERAL, "0", 0, 2, 7),
        Token(TokenType.SEMICOLON, ";", None, 2, 8),
        Token(TokenType.IDENTIFIER, "fin", None, 2, 13),
        Token(TokenType.EOF, "", None, 2, 16),
    ]
    assert result.tokens == expected_tokens

    expected_diagnostics = [
        Diagnostic("LEX001", "error", "Carácter no reconocido: '@'", 1, 9),
        Diagnostic("LEX001", "error", "Carácter no reconocido: '!'", 2, 3),
        Diagnostic("LEX001", "error", "Carácter no reconocido: '/'", 2, 10),
        Diagnostic("LEX001", "error", "Carácter no reconocido: '/'", 2, 11),
    ]
    assert result.diagnostics == expected_diagnostics

    formatted_tokens = [format_token(t) for t in result.tokens]
    assert formatted_tokens == [
        "KW_INT 'int' 1 1",
        "IDENTIFIER 'x' 1 5",
        "ASSIGN '=' 1 7",
        "SEMICOLON ';' 1 10",
        "IDENTIFIER 'x' 2 1",
        "ASSIGN '=' 2 5",
        "INTEGER_LITERAL '0' 2 7",
        "SEMICOLON ';' 2 8",
        "IDENTIFIER 'fin' 2 13",
        "EOF '' 2 16",
    ]

    formatted_diagnostics = [format_diagnostic(d) for d in result.diagnostics]
    assert formatted_diagnostics == [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]


def test_empty_source() -> None:
    result = Lexer("").scan()
    assert result.diagnostics == []
    assert len(result.tokens) == 1
    assert result.tokens[0] == Token(TokenType.EOF, "", None, 1, 1)


def test_whitespace_only() -> None:
    result = Lexer("   \t \r  \n  ").scan()
    assert result.diagnostics == []
    assert len(result.tokens) == 1
    assert result.tokens[0] == Token(TokenType.EOF, "", None, 2, 3)


def test_tab_counts_as_one_column() -> None:
    source = "\tint"
    result = Lexer(source).scan()
    assert result.tokens[0] == Token(TokenType.KW_INT, "int", None, 1, 2)


def test_keywords_vs_identifiers() -> None:
    source = "int while int_var while1 _int whilex"
    result = Lexer(source).scan()
    types = [t.type for t in result.tokens[:-1]]
    lexemes = [t.lexeme for t in result.tokens[:-1]]

    assert types == [
        TokenType.KW_INT,
        TokenType.KW_WHILE,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
        TokenType.IDENTIFIER,
    ]
    assert lexemes == ["int", "while", "int_var", "while1", "_int", "whilex"]


def test_operators_maximum_munch() -> None:
    source = "== = != !"
    result = Lexer(source).scan()

    assert [t.type for t in result.tokens] == [
        TokenType.EQUAL_EQUAL,
        TokenType.ASSIGN,
        TokenType.NOT_EQUAL,
        TokenType.EOF,
    ]
    assert len(result.diagnostics) == 1
    assert result.diagnostics[0] == Diagnostic(
        "LEX001", "error", "Carácter no reconocido: '!'", 1, 9
    )


def test_all_single_operators_and_delimiters() -> None:
    source = "= + - ( ) { } ;"
    result = Lexer(source).scan()

    expected_types = [
        TokenType.ASSIGN,
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert [t.type for t in result.tokens] == expected_types
    assert result.diagnostics == []


def test_integer_literals_and_values() -> None:
    source = "0 7 007 12345678901234567890"
    result = Lexer(source).scan()

    assert result.diagnostics == []
    tokens = result.tokens[:-1]
    assert [t.literal for t in tokens] == [0, 7, 7, 12345678901234567890]
    assert [t.lexeme for t in tokens] == ["0", "7", "007", "12345678901234567890"]


def test_consecutive_diagnostics_and_recovery() -> None:
    source = "$%#&"
    result = Lexer(source).scan()

    assert len(result.tokens) == 1
    assert result.tokens[0].type == TokenType.EOF
    assert len(result.diagnostics) == 4
    for i, char in enumerate("$%#&", start=1):
        assert result.diagnostics[i - 1] == Diagnostic(
            "LEX001", "error", f"Carácter no reconocido: '{char}'", 1, i
        )


def test_scan_idempotence() -> None:
    lexer = Lexer("int x = 1;")
    res1 = lexer.scan()
    res2 = lexer.scan()
    assert res1.tokens == res2.tokens
    assert res1.diagnostics == res2.diagnostics
