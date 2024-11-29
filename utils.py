import re
import papermill as pm


def load_last_measurements(file_path):
  try:
    with open(file_path, "r") as file:
      content = file.read()
      matches = re.findall(r"Peso: ([\d.]+) kg\nIdade: (\d+) anos\nAltura: ([\d.]+)", content)
      if matches:
        last_entry = matches[-1]
        peso = float(last_entry[0])
        idade = int(last_entry[1])
        altura = float(last_entry[2])
        return peso, idade, altura
      else:
        print("Nenhum dado encontrado no arquivo.")
        return None
  except FileNotFoundError:
    print("Arquivo não encontrado.")
    return None
    

def execute_notebook(input_path, output_path, parameters):
    try:
        pm.execute_notebook(
            input_path,
            output_path,
            parameters=parameters
        )
        print("Notebook executado com sucesso.")
    except Exception as e:
        print(f"Erro ao executar o notebook: {e}")