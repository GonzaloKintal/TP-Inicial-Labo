from generador_dataset.generator import generate_dataset
from generador_dataset.trainer import training_model

def main():
    print("Dataset generado:")
    df = generate_dataset()
    training_model(df)

if __name__ == "__main__":
    main()