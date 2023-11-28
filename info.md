# Language

With lisp flavour~~

## Syntax
```
program ::= s-expression

s-expression ::= atomic-symbol 
               | "(" s-expresssion " " s-expression ")" 

atomic-symbol ::= control-symbol
                | number
                | letter
                | empty
                | atomic-symbol atomic-symbol

control-symbol ::= "=" |  "-" | "+" 

letter ::= "a" | "b" | ... | "z"

number ::= "0" | "1" | ... | "9"

empty ::= ""
```


## Semantics

## Scopes
???

### Functions
- "set" [var] [s-exp] -> set result of [s-exp] to variable [var] 
- "print" [s-expression] -> print result of [s-expression]
- "=" [var | const] [var | const] -> compare operands values and return result
- "+", "-", "/", "*" [var | const] [var | const] -> [add, substract, divide, multiply] second operand's value [to, from, by, by] first operand's value then store new value in first operand (in case it's a [var]) and return result
- "%" [var | const] [const] -> return remainder of first operand value division by second

### Execution stream control
- if [base s-exp] [then s-exp] [else s-exp] -> if result of [base s-exp] is "positive" return [then s-exp]'s value else [else s-exp]'s. "Positive" means it either string or non-zero number.

for loop???
