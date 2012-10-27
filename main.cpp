#include <iostream.h>
#include <unistd.h>


void usage()
{
    std::cout << "run `Latte -h` for help";
}


int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        usage();
    }

    int opt;
    while ((opt = getopt(argc, argv, "h")) != -1)
    {
        switch(opt)
        {
            case 'h': 
                usage();
                break;
            default:
                break;
        }
    }


    return 0;
}
