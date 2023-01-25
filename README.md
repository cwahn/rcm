# RCM
Recursive Component Model implementation on Django ORM utilizing EWDAG.

## Concept
```bnf
Component ::= Part
           | 'set` (Component, N)
```

## Features
- No cyclic component definition
- No part only data for component
- No component only data for part
- No sub-component for part
- Number of parts of a component