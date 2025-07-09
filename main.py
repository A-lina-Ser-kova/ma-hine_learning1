import streamlit as st
import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# Настройки страницы
st.set_page_config(
    page_title="🍏 Анализатор пищевой ценности",
    page_icon="🍎",
    layout="wide"
)

@st.cache_resource
def load_model():
    """Загрузка модели"""
    try:
        model = joblib.load('Linear Regression.pkl')
        return model
    except Exception as e:
        st.error(f"Ошибка загрузки модели: {e}")
        return None

def prepare_input(input_data):
    """Подготовка входных данных для модели"""
    try:
        # Конвертируем единицы измерения (мг -> г)
        input_data['calcium'] /= 1000
        input_data['irom'] /= 1000
        input_data['potassium'] /= 1000
        input_data['sodium'] /= 1000
        input_data['cholesterol'] /= 1000
        
        # Создаем DataFrame в правильном порядке признаков
        features = pd.DataFrame([[
            input_data['protein'],
            input_data['fiber'],
            input_data['sugars'],
            input_data['fat'],
            input_data['carbohydrate'],
            input_data['calcium'],
            input_data['irom'],
            input_data['potassium'],
            input_data['sodium'],
            input_data['cholesterol']
        ]], columns=[
            'protein', 'fiber', 'sugars', 'fat', 'carbohydrate',
            'calcium', 'irom', 'potassium', 'sodium', 'cholesterol'
        ])
        
        return features
    except Exception as e:
        st.error(f"Ошибка подготовки данных: {e}")
        return None

def calculate_macros(protein, fat, carbs, calories):
    """Расчет вклада макронутриентов"""
    protein_cals = protein * 4
    fat_cals = fat * 9
    carb_cals = carbs * 4
    total = protein_cals + fat_cals + carb_cals
    
    if total > 0:
        return {
            'Белки': protein_cals,
            'Жиры': fat_cals,
            'Углеводы': carb_cals,
            '% Белки': protein_cals / total * 100,
            '% Жиры': fat_cals / total * 100,
            '% Углеводы': carb_cals / total * 100
        }
    return None

def main():
    st.title("🍏 Анализатор пищевой ценности")
    st.markdown("### Введите параметры продукта для оценки калорийности и пищевой ценности")
    
    model = load_model()
    if model is None:
        st.stop()

    # Создаем колонки для ввода данных
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Макронутриенты (г на 100г продукта)")
        protein = st.number_input("Белки", 0.0, 100.0, 10.0, 0.1)
        fat = st.number_input("Жиры", 0.0, 100.0, 5.0, 0.1)
        carbohydrate = st.number_input("Углеводы", 0.0, 100.0, 20.0, 0.1)
        fiber = st.number_input("Клетчатка", 0.0, 50.0, 2.0, 0.1)
        sugars = st.number_input("Сахара", 0.0, 100.0, 5.0, 0.1)

    with col2:
        st.subheader("Минералы (мг на 100г продукта)")
        calcium = st.number_input("Кальций", 0, 2000, 50)
        iron = st.number_input("Железо", 0, 100, 2)
        potassium = st.number_input("Калий", 0, 5000, 300)
        sodium = st.number_input("Натрий", 0, 5000, 100)
        cholesterol = st.number_input("Холестерин", 0, 1000, 0)

    if st.button("Рассчитать пищевую ценность", type="primary"):
        input_data = {
            'protein': protein,
            'fiber': fiber,
            'sugars': sugars,
            'fat': fat,
            'carbohydrate': carbohydrate,
            'calcium': calcium,
            'irom': iron,
            'potassium': potassium,
            'sodium': sodium,
            'cholesterol': cholesterol
        }

        features = prepare_input(input_data)
        
        if features is not None:
            try:
                # Предсказание
                predicted_calories = max(0, round(model.predict(features)[0]))
                
                # Результаты
                st.success(f"## Расчетная калорийность: {predicted_calories} ккал/100г")
                
                # Расчет макронутриентов
                macros = calculate_macros(protein, fat, carbohydrate, predicted_calories)
                
                if macros:
                    st.subheader("Распределение калорийности")
                    cols = st.columns(3)
                    cols[0].metric("Белки", f"{macros['% Белки']:.1f}%")
                    cols[1].metric("Жиры", f"{macros['% Жиры']:.1f}%")
                    cols[2].metric("Углеводы", f"{macros['% Углеводы']:.1f}%")
                    
                    # Визуализация
                    chart_data = pd.DataFrame({
                        "Макронутриенты": ["Белки", "Жиры", "Углеводы"],
                        "Калории": [macros['Белки'], macros['Жиры'], macros['Углеводы']]
                    })
                    st.bar_chart(chart_data, x="Макронутриенты", y="Калории")
                
                # Дополнительная информация
                with st.expander("Подробная информация"):
                    st.write("""
                    - **Калорийность на грамм**:
                      - Белки: 4 ккал/г
                      - Жиры: 9 ккал/г
                      - Углеводы: 4 ккал/г
                    """)
                    
            except Exception as e:
                st.error(f"Ошибка расчета: {e}")

if __name__ == "__main__":
    main()