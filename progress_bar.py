from tqdm import tqdm
import time

def demo_progress():
    # 100 шагов, от 0 до 100%
    for i in tqdm(range(101), desc="Прогресс", unit="%", ncols=80):
        time.sleep(0.03)  
    print("Готово!")

if __name__ == "__main__":
    demo_progress()