import pulp
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import japanize_matplotlib
from shift_scheduler import ShiftScheduler

# タイトル
st.title("シフトスケジューリングアプリ")

# サイドバー
st.sidebar.header("aデータのアップロード")
cal_file = st.sidebar.file_uploader("カレンダー")
staff_file = st.sidebar.file_uploader("スタッフ")

cal_df = pd.DataFrame()
staff_df = pd.DataFrame()

if cal_file is not None:
    cal_df = pd.read_csv(cal_file)

if staff_file is not None:
    staff_df = pd.read_csv(staff_file)

# タブ
tab1, tab2, tab3 = st.tabs(["カレンダー情報", "スタッフ情報", "シフト表作成"])

with tab1:
    if cal_df.empty:
        st.text("カレンダー情報をアップロードしてください")
    else:
        st.markdown("## カレンダー情報")
        st.dataframe(cal_df)
    

with tab2:
    if staff_df.empty:
        st.text("スタッフ情報をアップロードしてください")
    else:
        st.markdown("## スタッフ情報")
        st.dataframe(staff_df)

with tab3:
    if cal_df.empty:
        st.text("カレンダー情報をアップロードしてください")
    if staff_df.empty:
        st.text("スタッフ情報をアップロードしてください")

    if not cal_df.empty and not staff_df.empty:
        if st.button("最適化実行"):
            sch = ShiftScheduler()
            sch.set_data(staff_df, cal_df)
            sch.build_model()
            sch.solve()

            st.markdown("## 最適化結果")
            st.text(f"実行ステータス:{pulp.LpStatus[sch.status]}")
            st.text(f"最適値:{sch.model.objective.value()}")

            st.markdown("## シフト表")

            sch_df = sch.sch_df
            st.dataframe(sch_df)

            #st.markdown("## シフト数の充足確認")
            fig, ax = plt.subplots(1, 1)
            shift_num = sch_df.sum(axis=1)
            ax.set_title("シフト数の充足確認")
            ax.bar(shift_num.index, shift_num.to_numpy())
            st.pyplot(fig)

            #st.markdown("## スタッフの希望の確認")
            fig, ax = plt.subplots(1, 1)
            staff_num = sch_df.sum(axis=0)

            ax.set_title("スタッフの希望の確認")
            ax.bar(staff_num.index, staff_num.to_numpy())
            st.pyplot(fig)

            #st.markdown("## 責任者の合計シフト数の充足確認")
            manager_df = pd.merge(staff_df, sch_df.reset_index().rename(columns={'index': 'スタッフID'}), on='スタッフID')
            def sum_manager(c):
                total = 0
                for index in c.index:
                    if staff_df[staff_df['スタッフID'] == index]['責任者フラグ'].to_numpy()[0]:
                        total += c[index]
                return total

            manager_sr = sch_df.apply(sum_manager, axis=0)
            fig, ax = plt.subplots(1, 1)
            ax.set_title("責任者の合計シフト数の充足確認")
            ax.bar(manager_sr.index, manager_sr.to_numpy())
            st.pyplot(fig)


