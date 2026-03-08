import streamlit as st
from graph import graph

st.set_page_config(page_title="AI Jury & Judge", page_icon="⚖️", layout="wide")

st.title("⚖️ AI Jury & Judge Tartışma Sistemi")
st.markdown("""
Bu sistemde 3 farklı yapay zeka Jury Agent'ı, sorduğunuz soruyu kendi perspektiflerinden (Resmi/Tarihi, Sosyal Medya/Kamuoyu, Akademik/Bilimsel) ele alır. İnternette arama yaparak 3 tur boyunca kendi aralarında tartışırlar. Son olarak Judge Agent devreye girerek tüm argümanları sentezleyip nihai kararı verir ve Jury Agent'ları puanlar.
""")

user_query = st.text_input("Tartışılacak konuyu veya soruyu girin:", placeholder="Örn: Evden çalışma verimliliği düşürüyor mu, artırıyor mu?")

if st.button("Tartışmayı Başlat", type="primary"):
    if user_query.strip():
        # State'i başlat
        initial_state = {
            "user_message": user_query,
            "agent_history": [],
            "current_round": 0,
            "judge_output": None
        }

        status_text = st.empty()
        status_text.info("Tartışma başladı! Jury Agent'lar araştırıyor...")

        final_state = {
            "user_message": user_query,
            "agent_history": [],
            "current_round": 0,
            "judge_output": None
        }

        with st.status("Ajanların Çalışma Süreci...", expanded=True) as status:
            try:

                for event in graph.stream(initial_state, stream_mode="updates"):
                    for node_name, state_update in event.items():
                        if not isinstance(state_update, dict):
                            continue
                            
                        if "agent_history" in state_update and state_update["agent_history"]:
                            new_history = state_update["agent_history"]
                            final_state["agent_history"].extend(new_history)
                            for msg in new_history:
                                st.write(f"🧑‍⚖️ **{msg.get('agent_name', 'Bilinmeyen Ajan')}** tezini sundu! (Tur {final_state['current_round'] + 1})")
                        
                        if "current_round" in state_update:
                            final_state["current_round"] = state_update["current_round"]
                            st.write(f"🔄 **Tur {final_state['current_round']} tamamlandı**, diğer tura/karara geçiliyor...")
                            
                        if "judge_output" in state_update and state_update["judge_output"]:
                            final_state["judge_output"] = state_update["judge_output"]
                            st.write("⚖️ **Judge Agent** nihai kararını verdi!")
                            
                status.update(label="Tüm Ajan İşlemleri Tamamlandı!", state="complete", expanded=False)
                
            except Exception as e:
                status.update(label="Hata Oluştu", state="error", expanded=True)
                if "insufficient_quota" in str(e):
                    st.error("🚨 OpenAI API Bakiye Hatası! Krediniz bitmiş. Lütfen platform.openai.com üzerinden bakiye yükleyin.")
                else:
                    st.error(f"Beklenmeyen Hata: {str(e)}")
                st.stop() 

        if final_state:
            status_text.success("Tartışma tamamlandı ve karar verildi!")
            st.divider()

            st.header("🗣️ Jury Agent Tartışma Kayıtları (3 Tur)")
            history = final_state.get("agent_history", [])
            
            rounds = {}
            for item in history:
                r = item.get("round", 0)
                if r not in rounds:
                    rounds[r] = []
                rounds[r].append(item)

            for r in sorted(rounds.keys()):
                with st.expander(f"Tur {r + 1} - Jury Agent'ların Argümanları", expanded=True):
                    for msg in rounds[r]:
                        st.markdown(f"#### {msg.get('agent_name', 'Bilinmeyen Ajan')}")
                        st.markdown(f"**Tez:** {msg.get('thesis', '')}")
                        st.markdown(f"**Kanıt/Gerekçe:** {msg.get('reasoning', '')}")
                        
                        if msg.get('counter_thesis'):
                            st.markdown(f"**Karşıt Görüşe Eleştiri:** {msg.get('counter_thesis', '')}")
                        if msg.get('counter_reasoning'):
                            st.markdown(f"**Karşıt Görüşü Çürütme Gerekçesi:** {msg.get('counter_reasoning', '')}")
                        if msg.get('sources'):
                            st.markdown("**📚 Kaynaklar:**")
                            for source in msg.get('sources', []):
                                st.markdown(f"- {source}")
                            
                        st.markdown("---")

            st.divider()

            st.header("⚖️ Judge Agent'ın Nihai Kararı")
            judge = final_state.get("judge_output", {})
            
            if judge:
                st.subheader("Nihai Yanıt")
                st.success(judge.get("final_response", ""))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Judge Agent'ın Gerekçesi")
                    st.info(judge.get("reasoning", ""))
                with col2:
                    st.subheader("Judge Agent'ın Tezi Sentezi")
                    st.warning(judge.get("thesis", ""))

                st.divider()
                
                st.subheader("📚 Judge Agent'ın Seçtiği En İyi Kaynaklar")
                judge_sources = judge.get("sources", [])
                if judge_sources:
                    for source in judge_sources:
                        st.markdown(f"- {source}")
                else:
                    st.info("Judge Agent özel bir kaynak listesi sunmadı.")

                st.divider()
                st.subheader("🏆 Jury Agent'ların Performans Puanlaması")
                
                score_col1, score_col2, score_col3 = st.columns(3)
                
                with score_col1:
                    j1_score = judge.get("jury_1_score", "?")
                    st.metric(label="🏛️ Jury 1 (Resmi/Tarih)", value=f"{j1_score} / 10")
                    st.info(judge.get("jury_1_reason", "Puanlama yapılmadı."))
                    
                with score_col2:
                    j2_score = judge.get("jury_2_score", "?")
                    st.metric(label="🌐 Jury 2 (Kamuoyu)", value=f"{j2_score} / 10")
                    st.success(judge.get("jury_2_reason", "Puanlama yapılmadı."))
                    
                with score_col3:
                    j3_score = judge.get("jury_3_score", "?")
                    st.metric(label="🔬 Jury 3 (Akademik)", value=f"{j3_score} / 10")
                    st.warning(judge.get("jury_3_reason", "Puanlama yapılmadı."))
            else:
                st.warning("Judge Agent bir çıktı üretemeden tartışma sonlandı.")

    else:
        st.warning("Lütfen önce bir konu girin.")
