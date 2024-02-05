
import streamlit as st
import json
import ssl
from langchain import LLMChain
from typing import Any, List, Optional
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain import PromptTemplate
import httpx

# HCX 토큰 계산기 API 호출
from hcx_token_cal import token_completion_executor


API_KEY='API KEY !!!!!!!!!!!!!!!!!!!!!!!!1'
API_KEY_PRIMARY_VAL='API KEY PRIMARY VAL !!!!!!!!!!!!!!!!!!!!!!!!1'
REQUEST_ID='REQUEST ID !!!!!!!!!!!!!!!!!!!!!'
llm_url = 'your llm url !!!!!!!!!!'



SYSTEMPROMPT = """나는 특정 업종 음식점 사장님 이다.

특정 업종 음식점에 대한 사용자 리뷰에 답변하려고 한다. 
리뷰에 답변할 때는 사용자의 리뷰 내용과 주문한 메뉴를 기반으로 진심어린 감사의 마음을 전달하고, 
주문한 다른 메뉴들에 대해서도 관심을 표현하여 고객과의 소통을 강화하고자 한다.

<주의 사항>
1. 사용자가 여러 메뉴를 주문했을 경우, 리뷰에 언급된 메뉴에 대해 감사를 표현하고, 언급되지 않은 다른 메뉴에 대해서는 고객의 의견을 물어봄으로써 모든 메뉴에 대한 관심을 보여야 함.
2. 사용자의 리뷰가 긍정적일 경우 😊와 같은 긍정적 이모티콘을, 부정적일 경우 😔와 같은 부정적 이모티콘을 답변의 마지막에 삽입하여 고객의 감정에 공감하고 그에 맞는 태도를 보여주어야 함.

<예시>
사용자 주문 메뉴: 간짜장, 해물 짬뽕, 군만두
사용자 리뷰: 간짜장이 정말 맛있어요! 다음번에 또 시켜먹을 계획이에요!
사장님: 간짜장이 맛있었다니 정말 기쁩니다! 😊 해물 짬뽕과 군만두도 함께 즐겨주셨나요? 고객님의 소중한 의견을 듣고 싶어요. 다음 번에도 만족할 수 있는 서비스와 맛으로 보답하겠습니다. 감사합니다!"""

template = """사용자 주문 메뉴: {menu}
사용자 리뷰: {review}
사장님: """
    
    
    
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
 


class HCX_stream(LLM):
    @property
    def _llm_type(self) -> str:
        return "HyperClovaX"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        preset_text = [{"role": "system", "content": SYSTEMPROMPT}, {"role": "user", "content": prompt}]
        
        print('---------------------------------------------')
        print(preset_text)

        request_data = {
            'messages': preset_text,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 512,
            'temperature': 0.9,
            'repeatPenalty': 5.0,
            'stopBefore': [],
            'includeAiFilters': True
        }

        # def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': API_KEY,
            'X-NCP-APIGW-API-KEY': API_KEY_PRIMARY_VAL,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': REQUEST_ID,
            'Content-Type': 'application/json; charset=utf-8',
            # streaming 옵션 !!!!!
            'Accept': 'text/event-stream'
        }

        full_response = ""
        message_placeholder = st.empty()
        
        with httpx.stream(method="POST", 
                        url=llm_url,
                        json=request_data,
                        headers=headers, 
                        timeout=120) as res:
            for line in res.iter_lines():
                if line.startswith("data:"):
                    split_line = line.split("data:")
                    line_json = json.loads(split_line[1])
                    if "stopReason" in line_json and line_json["stopReason"] == None:
                        full_response += line_json["message"]["content"]
                        print('************************************************************')
                        print(full_response)
                        message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            return full_response


hcx_llm = HCX_stream()
prompt = PromptTemplate(template=template, input_variables=["menu", "review"])

hcx_llm_chain = LLMChain(prompt=prompt, llm=hcx_llm)

# if 'generated' not in st.session_state:
#     st.session_state['generated'] = []
 
# if 'past' not in st.session_state:
#     st.session_state['past'] = []
 
# with st.form('form', clear_on_submit=True):
#     # user_input_1 = st.text_input('사용자 주문 메뉴', '', key='menu')
#     # user_input_2 = st.text_input('사용자 리뷰', '', key='review')

#     user_input_1 = st.text_input('사용자 주문 메뉴', default_menu, key='menu')
#     user_input_2 = st.text_input('사용자 리뷰', default_review, key='review')

#     submitted = st.form_submit_button('사장님 답변')
 
#     if submitted and user_input_1 and user_input_2:
#         with st.spinner("Waiting for HyperCLOVA..."): 
#             response_text = hcx_llm_chain.predict(menu = user_input_1, review = user_input_2)

#             single_turn_text_json = {
#             "messages": [
#             {
#                 "role": "system",
#                 "content": template
#             },
#             {
#                 "role": "user",
#                 "content": user_input_1
#             },
#             {
#                 "role": "user",
#                 "content": user_input_2
#             },
#             {
#                 "role": "assistant",
#                 "content": response_text
#             }
#             ]
#             }
            
#             single_turn_text_token = token_completion_executor.execute(single_turn_text_json)
#             print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
#             print(single_turn_text_json)
#             single_turn_token_count = single_turn_text_token[0]['count'] + single_turn_text_token[1]['count'] + single_turn_text_token[2]['count'] + single_turn_text_token[3]['count']
#             single_turn_token_count = sum(token['count'] for token in single_turn_text_token[:4])

#             st.session_state.past.append({'menu': user_input_1, 'review': user_input_2})
#             # st.session_state.generated.append({'generated': response_text, 'token_count': single_turn_token_count})
#             st.session_state.generated.append({'generated': response_text})
 
#         if st.session_state['generated']:
#             for i in range(len(st.session_state['generated']) - 1, -1, -1):
#                 user_input = st.session_state['past'][i]
#                 response = st.session_state['generated'][i]

#                 message(f"사용자 주문 메뉴: {user_input['menu']}", is_user=True, key=str(i) + '_menu')
#                 message(f"사용자 리뷰: {user_input['review']}", is_user=True, key=str(i) + '_review')
#                 message(f"사장님 답변: {response['generated']}", is_user=False, key=str(i) + '_generated')
#                 message(f"총 토큰 수: {response['token_count']}", is_user=False, key=str(i) + '_token_count')




st.title("음식점 사장님 리뷰 자동 생성")
 
default_menu = '로스카츠, 히레카츠, 치즈카즈, 치즈볼, 연어덮밥'
default_review = '등심돈까스의 등심이 정말 흑돼지 처럼 맛있어요!!! 치즈카즈는 치즈가 정말 쫄깃해요~~ 다음에 또 시켜먹을게요!'

# 세션 상태 초기화
if 'reviews' not in st.session_state:
    st.session_state.reviews = []

with st.form('review_form', clear_on_submit=True):
    # 사용자 리뷰 및 별점 입력
    st.markdown("""
    <h2 style="font-size: 24px; display: inline-block; margin-right: 10px;">🧑 마라보이 님</h2>
    <span style="font-size: 16px; vertical-align: super;">3시간 전, 작성됨.</span>
""", unsafe_allow_html=True)
    st.markdown("""
    <style>
        .rating-container {
            display: flex;
            align-items: center;
            justify-content: flex-start;
        }
        .star-rating {
            color: gold;
            font-size: 20px; /* 별의 크기를 조절하려면 이 값을 변경하세요 */
            margin-right: 5px; /* 별과 텍스트 사이의 간격을 조절하려면 이 값을 변경하세요 */
        }
        .rating-label {
            font-size: 16px; /* 라벨 텍스트의 크기를 조절하려면 이 값을 변경하세요 */
            margin-right: 10px; /* 라벨과 별 사이의 간격을 조절하려면 이 값을 변경하세요 */
        }
        .rating-section {
            margin-right: 20px; /* 각 평점 섹션 사이의 간격을 조절하려면 이 값을 변경하세요 */
        }
    </style>
    <div class="rating-container">
        <div class="rating-section">
            <span class="rating-label">맛:</span>
            <span class="star-rating">&#9733;&#9733;&#9733;&#9733;&#9734;</span>
        </div>
        <div class="rating-section">
            <span class="rating-label">양:</span>
            <span class="star-rating">&#9733;&#9733;&#9733;&#9733;&#9733;</span>
        </div>
        <div class="rating-section">
            <span class="rating-label">배달:</span>
            <span class="star-rating">&#9733;&#9733;&#9733;&#9733;&#9734;</span>
        </div>
    </div>
""", unsafe_allow_html=True)

    user_review = st.text_area('', default_review)     
    menu_items = default_menu.split(', ')
    # menu_items 각 '#' 앞에 붙이기
    menu_items = ['#' + item for item in menu_items]
    st.markdown(f"""
    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
        {' '.join(f'<span class="menu-item" style="font-size: 16px; padding: 8px; background-color: #f0f2f6; border-radius: 5px;">{item}</span>' for item in menu_items)}
    </div>
""", unsafe_allow_html=True)
    # <br> 추가
    st.markdown('<br>', unsafe_allow_html=True)
    submit_review = st.form_submit_button('사장님 리뷰 등록')
    
    if submit_review and user_review:

        # 사장님 리뷰 생성
        st.markdown("""
    <h2 style="font-size: 24px; display: inline-block; margin-right: 10px;">🙋‍♂️ 사장님</h2>
    <span style="font-size: 16px; vertical-align: super;">지금, 작성됨.</span>
""", unsafe_allow_html=True)
        
        owner_response = hcx_llm_chain.predict(menu=default_menu, review=user_review)

