#include <iostream>

#include "core/greeter.h"
#include "foo.h"

int main()
{
    int result = add(1, 2);
    greet();
    std::cout << "Hello, C++ world! " << result << std::endl;
    return 0;
}
