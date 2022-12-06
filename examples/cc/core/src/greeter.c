#include "core/greeter.h"

#include "greeter-private.h"
#include <stdio.h>

// Declared in core/greeter.h
void greet(void)
{
    char symbol = greetingSymbol();
    printf("Greetings, world%c", symbol);
}

int add(int a, int b)
{
    return a + b;
}

// Declared in greeter-private.h
char greetingSymbol(void)
{
    return '!';
}