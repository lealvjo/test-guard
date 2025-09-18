#!/usr/bin/env python3
"""
Script para executar testes do projeto test-guard
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type=None, verbose=False, coverage=False):
    """
    Executa os testes do projeto
    
    Args:
        test_type (str): Tipo de teste ('unit', 'integration', 'all')
        verbose (bool): Executar em modo verboso
        coverage (bool): Gerar relatório de cobertura
    """
    
    # Comando base do pytest
    cmd = ['python', '-m', 'pytest']
    
    # Adicionar flags baseadas nos parâmetros
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=.', '--cov-report=html', '--cov-report=term-missing'])
    
    # Filtrar por tipo de teste
    if test_type == 'unit':
        cmd.extend(['-m', 'unit', 'tests/unit/'])
    elif test_type == 'integration':
        cmd.extend(['-m', 'integration', 'tests/integration/'])
    elif test_type == 'all':
        cmd.append('tests/')
    else:
        # Executar todos os testes por padrão
        cmd.append('tests/')
    
    print(f"Executando comando: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ Todos os testes passaram com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Alguns testes falharam!")
        return False
    except FileNotFoundError:
        print("❌ Erro: pytest não encontrado. Certifique-se de que está instalado.")
        return False


def install_dependencies():
    """Instala as dependências de teste"""
    print("Instalando dependências de teste...")
    try:
        subprocess.run(['pip', 'install', '-r', 'requirements-test.txt'], check=True)
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências!")
        return False
    except FileNotFoundError:
        print("❌ Erro: pip não encontrado!")
        return False


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Executar testes do projeto test-guard')
    parser.add_argument('--type', choices=['unit', 'integration', 'all'], 
                       help='Tipo de teste a executar')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Executar em modo verboso')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Gerar relatório de cobertura')
    parser.add_argument('--install', action='store_true',
                       help='Instalar dependências antes de executar os testes')
    
    args = parser.parse_args()
    
    # Verificar se estamos no diretório correto
    if not Path('main.py').exists():
        print("❌ Erro: Execute este script no diretório raiz do projeto!")
        sys.exit(1)
    
    # Instalar dependências se solicitado
    if args.install:
        if not install_dependencies():
            sys.exit(1)
    
    # Executar testes
    success = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
