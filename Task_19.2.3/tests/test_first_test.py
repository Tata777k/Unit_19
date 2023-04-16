import pytest
import sys
import os
sys.path.insert(0,os.getcwd())
from app.calculator import Calculator

class TestCalc:
    def setup_method(self):
        self.calc = Calculator
    def test_multiply_calculate_right(self):
        assert self.calc.multiply(self,2,3)==6
    def test_division_calculate_right(self):
         assert self.calc.division(self,12,2)==6
    def test_subtraction_calculate_right(self):
        assert self.calc.subtraction(self, 12,2)==10
    def test_adding_calculate_right(self):
        assert self.calc.adding(self,4,5)==9


