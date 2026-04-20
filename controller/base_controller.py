from functools import wraps
from flask import jsonify


class BaseController:
    """
    Classe base para controllers com funcionalidades comuns
    """
    
    @staticmethod
    def handle_request(func):
        """
        Decorator para tratamento padrão de erros em endpoints
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": f"Erro interno: {str(e)}"}), 500
        return wrapper
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """
        Valida se todos os campos obrigatórios estão presentes nos dados
        
        Args:
            data (dict): Dados a serem validados
            required_fields (list): Lista de campos obrigatórios
            
        Returns:
            tuple: (is_valid, error_response) - se is_valid=False, error_response contém a resposta de erro
        """
        if data is None:
            return False, (jsonify({"error": "Body da requisição é obrigatório"}), 400)

        if not isinstance(data, dict):
            return False, (jsonify({"error": "Body da requisição deve ser um objeto JSON"}), 400)

        for field in required_fields:
            if field not in data:
                return False, (jsonify({"error": f"Campo '{field}' é obrigatório"}), 400)
        return True, None
    
    @staticmethod
    def validate_required_params(request_args, required_params):
        """
        Valida se todos os parâmetros obrigatórios estão presentes na query string
        
        Args:
            request_args: request.args do Flask
            required_params (list): Lista de parâmetros obrigatórios
            
        Returns:
            tuple: (is_valid, error_response) - se is_valid=False, error_response contém a resposta de erro
        """
        for param in required_params:
            if param not in request_args:
                return False, (jsonify({"error": f"Parâmetro '{param}' é obrigatório"}), 400)
        return True, None
    
    @staticmethod
    def success_response(message, data=None, status_code=200):
        """
        Cria uma resposta de sucesso padronizada
        
        Args:
            message (str): Mensagem de sucesso
            data (dict): Dados adicionais (opcional)
            status_code (int): Código de status HTTP
            
        Returns:
            tuple: (response, status_code)
        """
        response = {"message": message}
        if data and isinstance(data, dict):
            response.update(data)
        elif data:
            # Se data não é um dict, adiciona como um campo separado
            response["data"] = data
        return jsonify(response), status_code
    
    @staticmethod
    def error_response(message, status_code=400):
        """
        Cria uma resposta de erro padronizada
        
        Args:
            message (str): Mensagem de erro
            status_code (int): Código de status HTTP
            
        Returns:
            tuple: (response, status_code)
        """
        return jsonify({"error": message}), status_code

