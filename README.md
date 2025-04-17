# Project_DC

어둠의 경로를 통해 디시인사이드 갤러리에 글이나 댓글을 많이 단 사람들의 순위를 텍스트 파일로 저했는데, 합산이 안되는 게 불편해서 합산해주는 프로그램을 직접 만들었습니다.

# DCRankingMerger
크롤러를 사용해 수집한 랭킹의 원본 json 파일을 합산하여 통합 랭킹 문서 생성(html)
# DCCommentMerger
크롤러를 사용해 수집한 랭킹의 원본 json 파일을 합산하여 통합 랭킹 문서 생성(html)
# DCtotalRanker
DCRankingMerger, DCCommentMerger에서 생성한 ```.gr.txt```, ```.cr.txt``` 파일을 통해 글/댓글 별 가중치를 적용한 통합 랭킹 문서 생성(html)

# Others
참고 프로젝트
dcinisde-crawler.ver.2 (by hanel2527)
DCRanking (by Ofox213)
