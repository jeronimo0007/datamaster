# Exemplo de implementação
class DataMasker:
    def mask_pii(self, data):
        return {
            'cpf': self._mask_cpf(data['cpf']),
            'email': self._mask_email(data['email']),
            'phone': self._mask_phone(data['phone']),
            'name': self._mask_name(data['name'])
        }
    
    def _mask_cpf(self, cpf):
        # 123.456.789-00 → ***.456.***-00
        return f"***.{cpf[4:6]}*.{cpf[8:10]}-{cpf[-2:]}"