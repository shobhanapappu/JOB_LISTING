from bs4 import BeautifulSoup

# Sample HTML content (representing the table structure provided)
html_content = """
<table>
	                            <caption><strong>어린이집 구인 상세보기</strong>의 제목, 시설유형, 시설장, 소재지, 담당자명, 담당자전화번호, 모집직종, 자격사항, 접수마감일, 작성일, 임금, 내용을 나타내는 표입니다.</caption>
	                            <colgroup>
	                                <col style="width:20%;">
	                                <col style="width:30%;">
	                                <col style="width:20%;">
	                                <col style="width:30%;">
	                            </colgroup>
	                            <tbody>
	                                <tr>
	                                    <th scope="row">제목</th>
	                                    <td colspan="3">
	                                        영아반 연장반교사를 모집합니다.&nbsp;
	                                    </td>
	                                </tr>
	                                <tr>
	                                    <th scope="row">어린이집명</th>
	                                    <td colspan="3">
	                                        스위트팰리스어린이집&nbsp;
	                                        
		                                        <a href="#none" title="새창" onclick="goInfoMove('26440000165');">
													<img src="https://img.childcare.go.kr/ccef/jeju/about/child_home.gif" alt="정보공시로 이동">
												</a>
	                                            
	                                        
	                                    </td>
	                                </tr>
	                                <tr> 
	                                    <th scope="row">시설유형</th>
	                                    <td colspan="3">
	                                        국공립
	                                        
	                                        
	                                        
	                                        
	                                        	 <!-- 2017.01.20 인천형 추가 -->
	                                    </td>
	                                </tr>
	                                <tr>
	                                    <th scope="row">시설장</th>
	                                    <td colspan="3">성혜영</td>
	                                </tr>
	                                <tr>
	                                    <th scope="row">소재지</th>
	                                    <td colspan="3">부산광역시 강서구 명지1동</td>
	                                </tr>
	                                <tr>
	                                    <th scope="row">담당자명</th>
	                                    <td>성혜영</td>
	                                    <th scope="row">팩스번호</th>
	                                    <td>051-292-8366</td>
	                                </tr>
	                                <tr>
	                                    <th scope="row">담당자전화번호</th>
	                                    <td>051-291-8366</td>
	                                    <th scope="row">담당자 이메일</th>
	                                    <td>lh2918366@naver.com</td>
	                                </tr>
	                                <tr>
	                                    <th scope="row">모집직종</th>
	                                    <td colspan="3">보육교사</td>
	                                </tr>
	                                <tr>
	                                    <th scope="row">연장보육반 전담교사</th>
	                                    <td colspan="3">
	                                    	예
	                                        
	                                    </td>
	                                </tr>
	                                <tr>
	                                    <th scope="row">자격사항</th>
	                                    <td colspan="3">보육교사 2급</td>
	                                </tr>
	                                <tr>
	                                    <th scope="row">접수마감일</th>
	                                    <td>2025-07-25</td>
	                                    <th scope="row">작성일</th>
	                                    <td>2025-07-13</td>
	                                </tr>
	                                <tr>
	                                    <th scope="row">임금</th>
	                                    <td colspan="3">
	                                        
		                                        
		                                        
		                                                    보육사업 지침 준용
		                                        
	                                        
	                                    </td>
	                                </tr>
									
									<tr>
									  <th scope="row">공유하기</th>
									  <td colspan="3">
									      <!-- 카카오스토리 공유하기 시작  -->
									      <div class="panel-body" style="float:left;">
									
									      <!-- 네이버 공유하기 시작  -->
									          <img src="https://img.childcare.go.kr/board/nv-share.png" alt="네이버공유하기" onclick="shareNv();" style="width:24px; height:24px; cursor:pointer" tabindex="0">
									      <!-- 네이버 공유하기 끝  -->
									
									      <!-- 카카오스토리 공유하기 시작  -->
									      <div id="kakaostory-share-button" style="float:left;"></div>
									      <script type="text/javascript">
									          // 스토리 공유 버튼을 생성합니다.
									          Kakao.Story.createShareButton({
									            container: '#kakaostory-share-button',
									            //스테이징 테스트 시 운영경로로 확인
									            //url: "http://seoul.childcare.go.kr/ccef/community/notice/NoticeSl.jsp?flag=Sl&BBSGB=48&JOSEQ=153131",
									            url: window.location.href + '?flag=Sl&BBSGB=' + sfrm.BBSGB.value + '&JOSEQ=' + sfrm.JOSEQ.value,
									            text: document.sfrm.BTITLE.value
									          });
									      </script>
									      <!-- 카카오스토리 공유하기 끝  -->
									
									      <!-- 페이스북 공유하기 시작  -->
									          <img src="https://img.childcare.go.kr/board/fb-share.png" alt="페이스북공유하기" onclick="shareFb();" style="width:24px; height:24px; cursor:pointer" tabindex="0">
									      <!-- 페이스북 공유하기 끝  -->
									
									      <!-- 밴드 공유하기 시작  -->
									          <img src="https://img.childcare.go.kr/board/band-share.png" alt="밴드공유하기" onclick="shareBand();" style="width:24px; height:24px; cursor:pointer" tabindex="0">
									      <!-- 밴드 공유하기 끝  -->
									      </div>
									  </td>
									</tr>

	                                <tr>
	                                    <td colspan="4" class="con_con">
		                                    
	                                            
	                                                
	                                                사랑스러운 영아반의 연장반전담교사(인건비지원)를 모집합니다.
<br>
<br>1.자격-보육교사자격증소지자, 결격사유없는자, 장기미종사교육이수자
<br>
<br>2.제출서류-이력서(사진부착), 자기소개서, 경력증명서, 장기미종사교육이수증(해당교사)
<br>
<br>3.즐겁게 오래 근무할 교사를 모집합니다. 
<br>
<br>4.서류접수 후 개별 연락을 통해 면접 진행
<br>   
<br> *제출서류는 일제 반환하지 않으며, 채용외의 목적으로 사용하지 않음.
<br>
<br> *서류전형 불합격자에게는 별도 통지가 없음
<br>
<br> *서류제출시 개인정보보호법에 동의한 것으로 간주함. 
	                                                  
	                                            
	                                            
	                                        
	                                    </td>
	                                </tr>
	                            </tbody>
	                        </table>
"""

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table
table = soup.find('table')

# Get all rows from the table body
rows = table.find('tbody').find_all('tr')

# Initialize variables to store the required data
name = ""
region = ""
email = ""
facility_type = ""

# Extract data based on row positions
# 3rd row: Type (시설유형, only TD text, ignoring span)
type_row = rows[2]  # 3rd row (index 2)
facility_type = type_row.find('td').contents[0].strip()  # Get only the text before the span

# 5th row: Region (소재지)
region_row = rows[4]  # 5th row (index 4)
region = region_row.find('td').text.strip()

# 6th row: Name (담당자명)
name_row = rows[5]  # 6th row (index 5)
name = name_row.find_all('td')[0].text.strip()  # First TD for 담당자명

# 7th row: Email (담당자 이메일)
email_row = rows[6]  # 7th row (index 6)
email = email_row.find_all('td')[1].text.strip()  # Second TD for 담당자 이메일

# Print the extracted data
print(f"Name: {name}")
print(f"Region: {region}")
print(f"Email: {email}")
print(f"Type: {facility_type}")