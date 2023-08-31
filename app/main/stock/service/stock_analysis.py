"""

"""
from app.main.stock.dao.stock_dao import get_stock_detail


def run():
    codes = ['600183', '600892', '601366', '603196', '603222', '603629', '605168', '688682', '000049', '002168', '002214', '002396', '002568', '002762', '002858', '003039', '300076', '300115', '300236', '300280', '300292', '300322', '300346', '300502', '300555', '300631', '300712', '300852', '300857', '300985']
    company_map = get_stock_detail(codes)

    concept_map = {}

    for code,detail in company_map.items():
        for concept in detail['concept']:
            if concept not in concept_map.keys():
                concept_map[concept] = list()
            concept_map[concept].append(code)
    pass

if __name__ == "__main__":
    run()