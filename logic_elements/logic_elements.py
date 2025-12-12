class TLogicElement:
    def __init__(self):
        self.__input1 = False
        self.__input2 = False
        self._result = False
        self.__nextElem = None
        self.__nextInput = 0

        if not hasattr(self, 'calc'):
            raise NotImplementedError("You can`t make this object!")

    def __setInput1(self, newInput1):
        self.__input1 = newInput1
        self.calc()
        if self.__nextElem:
            if self.__nextInput == 1:
                self.__nextElem.Input1 = self._result
            elif self.__nextInput == 2:
                self.__nextElem.Input2 = self._result


    def __setInput2(self, newInput2):
        self.__input2 = newInput2
        self.calc()
        if self.__nextElem:
            if self.__nextInput == 1:
                self.__nextElem.Input1 = self._result
            elif self.__nextInput == 2:
                self.__nextElem.Input2 = self._result

    def link (self, nextElem, nextInput):
        self.__nextElem = nextElem
        self.__nextInput = nextInput

    Input1 = property(lambda x: x.__input1, __setInput1)
    Input2 = property(lambda x: x.__input2, __setInput2)
    Result = property(lambda x: x._result)

class TNot (TLogicElement):
    def __init__(self):
        super().__init__()
    
    def calc(self):
        self._result= not self.Input1

class TLogic2Input (TLogicElement):
    pass

class TAnd (TLogic2Input):
    def __init__(self):
        super().__init__()
    
    def calc (self):
        self._result = self.Input1 and self.Input2

class TOr (TLogic2Input):
    def __init__(self):
        super().__init__()

    def calc (self):
        self._result = self.Input1 or self.Input2

class TXor (TLogic2Input):
    def __init__(self):
        super().__init__()
    def calc(self):
        n1 = TNot()
        n2 = TNot()
        o1 = TOr()
        o2 = TOr()
        a = TAnd()

        o1.Input1 = self.Input1
        o1.Input2 = self.Input2

        n1.Input1 = self.Input1
        n2.Input1 = self.Input2

        o2.Input1 = n1.Result
        o2.Input2 = n2.Result

        a.Input1 = o1.Result
        a.Input2 = o2.Result

        self._result = a.Result

print("NAND")
elNot1 = TNot() 
elAnd1 = TAnd() 
print ( "  A | B | not(A&B) " )
print ( "-------------------" )
for A in range(2): 
  elAnd1.Input1 = bool(A) 
  for B in range(2): 
    elAnd1.Input2 = bool(B) 
    elNot1.Input1 = elAnd1.Result 
    print ( " ", A, "|", B, "|", int(elNot1.Result) )

print('\n'*5 + "Xor")

elNot3 = TNot()
elAnd3 = TAnd()
elOr3 = TOr()
print ( "  A | B | A xor B " )
print ( "-------------------" )
for A in range(2): 
  elOr3.Input1 = bool(A) 
  for B in range(2): 
    elOr3.Input2 = bool(B) 
    elAnd3.Input1 = elOr3.Result

    elNot3.Input1 = bool(A)
    elOr3.Input1 = elNot3.Result
    elNot3.Input1 = bool(B)
    elOr3.Input2 = elNot3.Result
    elAnd3.Input2 = elOr3.Result
    print ( " ", A, "|", B, "|", int(elAnd3.Result) )

print('\n'*5 + "Xor with class TXor")
elXor = TXor()
print ( "  A | B | A xor B " )
print ( "-------------------" )
for A in range(2): 
  elXor.Input1 = bool(A) 
  for B in range(2): 
    elXor.Input2 = bool(B)
    print ( " ", A, "|", B, "|", int(elXor.Result) )