import pandas as pd
from pathlib import Path

print(pd.__version__)


def test_pandas():
    """Test pandas"""
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    print(df.shape)
    assert df.shape == (2, 3)
    print(df)


def test_load_excel():
    """Test load excel"""
    filename = "C:/Users/rescobar/OneDrive - Carhartt Inc/Documents/git/powerbi-automate/data/Excel para automatización/Sin conexión a Supply-solo datos.xlsx"
    df = pd.read_excel(filename, sheet_name="Sheet1")
    # for index, row in df.iterrows():
    #     print(row['Código de producto'], row['Cantidad'])
    print(df)
    suma = 0
    expected = 0
    for _, row in df.iterrows():
        if row["Row Labels"] != "Grand Total":
            suma += row["Sales Demand Units"]
        else:
            expected = row["Sales Demand Units"]

    if suma == expected:
        print("OK")
    else:
        print(
            "Error: {} != {} there is a difference of {}".format(
                suma, expected, suma - expected
            )
        )


def main():
    test_load_excel()


if __name__ == "__main__":
    main()
    # test_pandas()
    # test_load_excel()
