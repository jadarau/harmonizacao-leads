"""Tests for Electric Vehicle Security Expert configuration."""
import pytest
from app.core.config import settings


class TestEVSecurityConfiguration:
    """Test Electric Vehicle Security Expert configuration."""
    
    def test_system_role_description_exists(self):
        """Test that system role description is configured."""
        assert hasattr(settings, 'system_role_description')
        assert settings.system_role_description is not None
        assert len(settings.system_role_description) > 0
    
    def test_system_role_description_content(self):
        """Test that system role description mentions electric vehicles and security."""
        role_desc = settings.system_role_description.upper()
        
        # Check for key terms in the role description
        assert any(term in role_desc for term in ['ELÉTRICO', 'ELETRICO', 'ELETRIFICADO']), \
            "System role should mention electric/electrified vehicles"
        assert any(term in role_desc for term in ['SEGURANÇA', 'SEGURANCA', 'SECURITY']), \
            "System role should mention security/safety"
        assert any(term in role_desc for term in ['ESPECIALISTA', 'EXPERT']), \
            "System role should position as an expert"
    
    def test_system_role_is_configurable(self):
        """Test that system role can be configured via environment."""
        # This test verifies the configuration exists and can be read
        # In actual deployment, it would be set via .env file
        assert isinstance(settings.system_role_description, str)
    
    def test_default_system_role_matches_requirement(self):
        """Test that default system role matches the problem statement."""
        role_desc = settings.system_role_description
        
        # Verify it matches the requirement from problem statement
        # The requirement is: "VOCÊ É UM ESPECIALISTA EM SEGURANÇA COM VEÍCULOS ELÉTICOS E ELETRIFICADOS"
        assert 'ESPECIALISTA' in role_desc or 'especialista' in role_desc
        assert 'SEGURANÇA' in role_desc or 'segurança' in role_desc
        assert ('ELÉTRICO' in role_desc or 'elétrico' in role_desc or 
                'ELETRICO' in role_desc or 'eletrico' in role_desc)
        assert 'ELETRIFICADO' in role_desc or 'eletrificado' in role_desc
