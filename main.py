from algorithms.cdnn import gen_models

def main():
    gen_models(12, 24, 3, (0.01, 0.1), (0.01, 0.2), 5000)

if __name__ == '__main__':
    main()
