# -*- coding: utf-8 -*-
"""
taxonomy.py — Bảng tra cứu chuẩn 70 cây thuốc nam QĐ4664/QĐ-BYT 2014.
Dùng chung cho toàn bộ pipeline VNHerb-70.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass(frozen=True)
class Taxon:
    id: int
    vi: str            # Tên Việt Nam
    sci: str           # Tên khoa học
    family: str        # Họ thực vật
    organs_qd: str     # Bộ phận dùng theo QĐ4664
    synonyms: str      # Tên đồng nghĩa
    local: str         # Tên địa phương các vùng

    @property
    def genus(self) -> str:
        return self.sci.split()[0].strip(".,")

    @property
    def species_epithet(self) -> str:
        parts = self.sci.split()
        return parts[1].strip(".,") if len(parts) > 1 else ""

    @property
    def slug_id(self) -> str:
        return f"{self.id:02d}"


# (id, vi, sci, family, organs_qd, synonyms, local)
_RAW = [
    (1, "Bạc hà", "Mentha arvensis L.", "Bạc hà (Lamiaceae)", "Bộ phận trên mặt đất",
     "Bạc hà nam; Bạc hà á", "nạt nặm, chạ phiéc hom (Tày)"),
    (2, "Bách bộ", "Stemona tuberosa Lour.", "Bách bộ (Stemonaceae)", "Rễ (rễ củ)",
     "Củ ba mươi; dây đẹt ác; Dây ba mươi", "hơ linh (Ba Na)"),
    (3, "Bạch đồng nữ", "Clerodendrum chinense (Osbeck) Mabb. var. simplex", "Cỏ roi ngựa (Verbenaceae)",
     "Rễ, lá, hoa", "Mò trắng; Mò mâm xôi; Bấn trắng", ""),
    (4, "Bạch hoa xà thiệt thảo", "Hedyotis diffusa Willd.", "Cà phê (Rubiaceae)", "Toàn cây",
     "Cỏ lưỡi rắn hoa trắng; Bồi ngòi bò", ""),
    (5, "Bán hạ nam", "Typhonium trilobatum (L.) Schott", "Ráy (Araceae)", "Thân rễ (qua chế biến)",
     "Cây chóc; chóc chuột; nam tinh; bán hạ ba thùy", ""),
    (6, "Bố chính sâm", "Abelmoschus moschatus Medik. ssp. tuberosus", "Bông (Malvaceae)", "Rễ",
     "Nhân sâm Phú Yên; Thổ hào sâm; Sâm bố chính", ""),
    (7, "Bồ công anh", "Lactuca indica L.", "Cúc (Asteraceae)", "Phần trên mặt đất",
     "Diếp dại; diếp trời; rau bồ cóc; rau mét; cây mũi mác", ""),
    (8, "Cà gai leo", "Solanum procumbens Lour.", "Cà (Solanaceae)", "Rễ, dây",
     "Cà vạnh; Cà cườm; Cà quánh; Cà quýnh; Cà gai dây", ""),
    (9, "Cam thảo đất", "Scoparia dulcis L.", "Hoa mõm chó (Scrophulariaceae)", "Cả cây",
     "Cam thảo nam; thổ cam thảo; dã cam thảo", "r'gờm, t'rôm lạy (K'Ho)"),
    (10, "Cỏ mần trầu", "Eleusine indica (L.) Gaertn.", "Lúa (Poaceae)", "Cả cây",
     "Cỏ chỉ tía; thanh tâm thảo; Ngưu cân thảo", "cao dag (Ba Na), hất t'rớ lạy (K'Ho)"),
    (11, "Cỏ nhọ nồi", "Eclipta prostrata (L.) L.", "Cúc (Asteraceae)", "Phần trên mặt đất",
     "Cỏ mực; Hạn liên thảo; lệ trường; phong trường", "mạy mỏ lắc nà (Tày), nhả cha chát (Thái)"),
    (12, "Cỏ sữa lá nhỏ", "Euphorbia thymifolia L.", "Thầu dầu (Euphorbiaceae)", "Cả cây",
     "Vú sữa đất; thiên căn thảo; cẩm địa", ""),
    (13, "Cỏ tranh", "Imperata cylindrica (L.) Beauv.", "Lúa (Poaceae)", "Thân rễ",
     "Bạch mao căn; Cỏ tranh răng", "dia (K'Dong), nhất địa (Gia Rai)"),
    (14, "Cỏ xước", "Achyranthes aspera L.", "Rau dền (Amaranthaceae)", "Rễ (phơi/sấy khô)",
     "Hoài ngưu tất; Ngưu tất nam", ""),
    (15, "Cối xay", "Abutilon indicum (L.) Sweet", "Bông (Malvaceae)", "Bộ phận trên mặt đất",
     "Giàng xay; quýnh ma; ma bản thảo; kim hoa thảo", ""),
    (16, "Cốt khí", "Reynoutria japonica Houtt.", "Rau răm (Polygonaceae)", "Rễ (phơi/sấy khô)",
     "Cốt khí củ; Hổ trượng căn; Điền thất", ""),
    (17, "Cúc hoa", "Chrysanthemum indicum L.", "Cúc (Asteraceae)", "Cụm hoa",
     "Kim cúc; hoàng cúc; dã cúc; cam cúc; Cúc hoa vàng", ""),
    (18, "Cúc tần", "Pluchea indica (L.) Less.", "Cúc (Asteraceae)", "Rễ, lá, cành",
     "Cây lức; từ bi; Đại bi", "phật phà (Tày)"),
    (19, "Dành dành", "Gardenia jasminoides J. Ellis", "Cà phê (Rubiaceae)", "Quả (đã phơi khô)",
     "Chi tử; Sơn chi tử", ""),
    (20, "Dâu tằm", "Morus alba L.", "Dâu tằm (Moraceae)", "Rễ, thân (cành), lá, quả",
     "Dâu ta; Tang (Tang bạch bì, Tang diệp, Tang chi, Tang thầm)", ""),
    (21, "Địa hoàng", "Rehmannia glutinosa (Gaertn.) Libosch.", "Hoa mõm chó (Scrophulariaceae)",
     "Rễ củ (phơi/sấy khô)", "Sinh địa hoàng; Sinh địa; Thục địa", ""),
    (22, "Địa liền", "Kaempferia galanga L.", "Gừng (Zingiberaceae)", "Thân rễ, lá",
     "Sơn nại; tam nại; thiền liền; sa khương", ""),
    (23, "Diệp hạ châu", "Phyllanthus urinaria L.", "Thầu dầu (Euphorbiaceae)", "Phần trên mặt đất",
     "Diệp hạ châu đắng; Cây chó đẻ răng cưa; Trân châu thảo", ""),
    (24, "Đinh lăng", "Polyscias fruticosa (L.) Harms", "Nhân sâm (Araliaceae)", "Rễ, thân, cành, lá",
     "Cây gỏi cá; nam dương sâm", ""),
    (25, "Đơn lá đỏ", "Excoecaria cochinchinensis Lour.", "Thầu dầu (Euphorbiaceae)", "Rễ, vỏ thân, lá",
     "Đơn đỏ; Đơn tía; Đơn mặt trời", ""),
    (26, "Dừa cạn", "Catharanthus roseus (L.) G. Don", "Trúc đào (Apocynaceae)", "Thân, lá, rễ",
     "Hải đằng; Dương giác; trường xuân hoa; Bông dừa", ""),
    (27, "Gai", "Boehmeria nivea (L.) Gaudich.", "Gai (Urticaceae)", "Rễ, lá",
     "Gai làm bánh; gai tuyết; trư ma; Trữ ma", ""),
    (28, "Gừng", "Zingiber officinale Rosc.", "Gừng (Zingiberaceae)", "Thân rễ (củ)",
     "Khương; Sinh khương; Can khương; Bào khương; Tiêu khương; Thán khương", ""),
    (29, "Hạ khô thảo", "Prunella vulgaris L.", "Bạc hà (Lamiaceae)", "Cụm quả (phơi/sấy khô)",
     "Hạ khô thảo; Mạch hạ khô", ""),
    (30, "Hoắc hương", "Pogostemon cablin (Blanco) Benth.", "Bạc hà (Lamiaceae)", "Lá (phơi/sấy khô)",
     "Thổ hoắc hương; Quảng hoắc hương", ""),
    (31, "Húng chanh", "Plectranthus amboinicus (Lour.) Spreng.", "Bạc hà (Lamiaceae)",
     "Lá tươi hoặc phần trên mặt đất (cất tinh dầu)", "Dương tử tô; Rau thơm lông; Tần dày lá", ""),
    (32, "Hương nhu tía", "Ocimum tenuiflorum L.", "Bạc hà (Lamiaceae)", "Bộ phận trên mặt đất",
     "É tía; É đỏ; Hương nhu", ""),
    (33, "Huyết dụ", "Cordyline fruticosa (L.) Goepp.", "Huyết giác (Dracaenaceae)", "Lá (tươi hoặc khô)",
     "Thiết thụ; Phật dụ; Long huyết", ""),
    (34, "Hy thiêm", "Siegesbeckia orientalis L.", "Cúc (Asteraceae)", "Phần trên mặt đất",
     "Cỏ đĩ; Cây cứt lợn; Hy tiên; Hy thiêm thảo", ""),
    (35, "Ích mẫu", "Leonurus japonicus Houtt.", "Bạc hà (Lamiaceae)", "Bộ phận trên mặt đất, hạt",
     "Cây chói đèn; sung úy; Ích mẫu thảo; Sung úy tử (hạt)", ""),
    (36, "Ké đầu ngựa", "Xanthium strumarium L.", "Cúc (Asteraceae)", "Quả già",
     "Thương nhĩ; Thương nhĩ tử", ""),
    (37, "Khổ sâm cho lá", "Croton tonkinensis Gagnep.", "Thầu dầu (Euphorbiaceae)",
     "Lá và cành (phơi khô)", "Khổ sâm Bắc bộ; cù đèn", "co chạy đón (Thái)"),
    (38, "Kim ngân", "Lonicera japonica Thunb.", "Kim ngân (Caprifoliaceae)", "Thân, lá, hoa",
     "Dây nhẫn đông; Nhẫn đông; Kim ngân hoa", "chừa giang khằn (Thái), boóc kim ngằn (Tày)"),
    (39, "Kim tiền thảo", "Desmodium styracifolium (Osbeck) Merr.", "Đậu (Fabaceae)",
     "Bộ phận trên mặt đất", "Đồng tiền lông; mắt trâu; vảy rồng; Mắt rồng", ""),
    (40, "Kinh giới", "Elsholtzia ciliata (Thunb.) Hyland.", "Bạc hà (Lamiaceae)",
     "Bộ phận trên mặt đất (ngọn mang hoa)", "Khương giới; giả tô; Kinh giới tuệ", "nhả nát hom (Thái)"),
    (41, "Lá lốt", "Piper lolot C. DC.", "Hồ tiêu (Piperaceae)", "Toàn cây", "Tất bát", ""),
    (42, "Mã đề", "Plantago major L.", "Mã đề (Plantaginaceae)", "Lá, hạt",
     "Xa tiền; bông mã đề; Xa tiền thảo (lá); Xa tiền tử (hạt)", ""),
    (43, "Mạch môn", "Ophiopogon japonicus (L.f.) Ker-Gawl.", "Mạch môn (Asparagaceae)",
     "Rễ củ (phơi/sấy khô)", "Mạch môn đông; mạch đông; tóc tiên; cỏ lan", ""),
    (44, "Mần tưới", "Eupatorium fortunei Turcz.", "Cúc (Asteraceae)", "Phần trên mặt đất (phơi/sấy khô)",
     "Lan thảo; hương thảo; Trạch lan", ""),
    (45, "Mỏ quạ", "Maclura cochinchinensis (Lour.) Corner", "Dâu tằm (Moraceae)", "Lá, rễ",
     "Hoàng lồ; Vàng lồ; Xuyên phá thạch", ""),
    (46, "Mơ tam thể", "Paederia lanuginosa Wall.", "Cà phê (Rubiaceae)", "Lá",
     "Mơ lông; Mơ tròn; Ngưu bì đống", ""),
    (47, "Náng", "Crinum asiaticum L.", "Thuỷ tiên (Amaryllidaceae)", "Lá, thân hành",
     "Lá náng; Náng hoa trắng; Đại tướng quân; Tỏi lơi", ""),
    (48, "Ngải cứu", "Artemisia vulgaris L.", "Cúc (Asteraceae)", "Bộ phận trên mặt đất",
     "Thuốc cứu; ngải diệp", "nhả ngải (Tày), quá sú (H'Mông), co linh li (Thái)"),
    (49, "Nghệ", "Curcuma longa L.", "Gừng (Zingiberaceae)", "Thân rễ (củ)",
     "Nghệ vàng; Khương hoàng (củ cái); Uất kim (củ nhánh)", "Co hem, Co khản mỉn (Thái)"),
    (50, "Ngũ gia bì chân chim", "Schefflera heptaphylla (L.) Frodin", "Nhân sâm (Araliaceae)", "Vỏ thân",
     "Cây chân chim; Cây đáng; Cây lằng; Sâm non; Ngũ gia bì", ""),
    (51, "Nhân trần", "Adenosma caeruleum R. Br.", "Hoa mõm chó (Scrophulariaceae)",
     "Bộ phận trên mặt đất", "Chè cát; chè nội; tuyến hương; Nhân trần tía", ""),
    (52, "Nhót", "Elaeagnus latifolia L.", "Nhót (Elaeagnaceae)", "Lá, quả, rễ",
     "Cây lót; hồi đồi tử", ""),
    (53, "Ổi", "Psidium guajava L.", "Sim (Myrtaceae)", "Lá, quả", "Ủi; phan thạch lựu", ""),
    (54, "Phèn đen", "Phyllanthus reticulatus Poir.", "Thầu dầu (Euphorbiaceae)", "Lá, vỏ thân cây",
     "Nỗ; Tạo phan diệp; Mực", ""),
    (55, "Quýt", "Citrus reticulata Blanco", "Cam (Rutaceae)", "Lá, vỏ, quả, hạt",
     "Quýt xiêm; quất thực; Trần bì (vỏ chín); Thanh bì (vỏ xanh); Quất hạch (hạt); Quất diệp (lá)", ""),
    (56, "Rau má", "Centella asiatica (L.) Urban", "Hoa tán (Apiaceae)", "Cả cây",
     "Liên tiền thảo; Tích tuyết thảo", ""),
    (57, "Râu mèo", "Orthosiphon spiralis (Lour.) Merr.", "Bạc hà (Lamiaceae)", "Phần trên mặt đất",
     "Cây bông bạc; Mao trao thảo", ""),
    (58, "Rau sam", "Portulaca oleracea L.", "Rau sam (Portulacaceae)", "Phần trên mặt đất",
     "Mã xỉ hiện; Trường thọ thái", ""),
    (59, "Sả", "Cymbopogon spp.", "Lúa (Poaceae)", "Thân rễ và lá", "Hương mao; Cỏ sả; Sả chanh", ""),
    (60, "Sài đất", "Wedelia chinensis (Osbeck) Merr.", "Cúc (Asteraceae)", "Bộ phận trên mặt đất",
     "Cúc nháp; ngổ núi; tân sa; Húng trám", ""),
    (61, "Sắn dây", "Pueraria thomsonii Benth.", "Đậu (Fabaceae)", "Rễ củ (phơi/sấy khô)",
     "Cát căn; Bạch cát; Khau cát", ""),
    (62, "Sim", "Rhodomyrtus tomentosa (Aiton) Hassk.", "Sim (Myrtaceae)", "Búp, lá, quả, rễ",
     "Hồng sim; Đào kim nương; Cương nhẫm; Dương lê", ""),
    (63, "Thiên môn đông", "Asparagus cochinchinensis (Lour.) Merr.", "Thiên môn (Asparagaceae)",
     "Rễ củ (phơi/sấy khô)", "Thiên môn; Tóc tiên leo; Dây tóc tiên; Thiên đông", ""),
    (64, "Tía tô", "Perilla frutescens (L.) Britton", "Bạc hà (Lamiaceae)",
     "Lá (Tô diệp), cành (Tô ngạnh), quả/hạt (Tô tử)", "Tử tô; Tô diệp; Tô ngạnh; Tô tử", ""),
    (65, "Trắc bách diệp", "Platycladus orientalis (L.) Franco", "Trắc bách (Cupressaceae)",
     "Lá (cành lá), hạt (Bá tử nhân)", "Trắc bá; Bá tử nhân (hạt)", ""),
    (66, "Trinh nữ hoàng cung", "Crinum latifolium L.", "Thuỷ tiên (Amaryllidaceae)", "Lá",
     "Náng lá rộng; Tỏi lơi lá rộng; Tây nam văn châu lan", ""),
    (67, "Xạ can", "Belamcanda chinensis (L.) DC.", "Lay ơn (Iridaceae)", "Thân rễ",
     "Rẻ quạt; Lưỡi đòng; Quạt", ""),
    (68, "Xích đồng nam", "Clerodendrum japonicum (Thunb.) Sweet", "Cỏ roi ngựa (Verbenaceae)",
     "Rễ, lá, hoa", "Mò đỏ; Mò mâm xôi đỏ; Bấn đỏ; Lẹo cái", ""),
    (69, "Xuyên tâm liên", "Andrographis paniculata (Burm. f.) Nees", "Ô rô (Acanthaceae)",
     "Bộ phận trên mặt đất", "Công cộng; Khổ đảm thảo; Lam khái liên; Nguyễn cộng", ""),
    (70, "Ý dĩ", "Coix lacryma-jobi L.", "Lúa (Poaceae)", "Hạt (Ý dĩ nhân)",
     "Bo bo; Cườm gạo; Dĩ mễ; Ý dĩ nhân", ""),
]

TAXA: List[Taxon] = [Taxon(*r) for r in _RAW]
BY_ID: Dict[int, Taxon] = {t.id: t for t in TAXA}

_GENUS_INDEX: Dict[str, List[Taxon]] = {}
for _t in TAXA:
    _GENUS_INDEX.setdefault(_t.genus.lower(), []).append(_t)


# ---- Cặp loài dễ nhầm (P6 confusion_risk) ----
CONFUSION_PAIRS = [
    (28, 49, "Zingiberaceae — Gừng vs Nghệ (thân rễ rất giống)"),
    (22, 49, "Zingiberaceae — Địa liền vs Nghệ"),
    (22, 28, "Zingiberaceae — Địa liền vs Gừng"),
    (23, 54, "Phyllanthus — Diệp hạ châu vs Phèn đen"),
    (3, 68, "Clerodendrum — Bạch đồng nữ (trắng) vs Xích đồng nam (đỏ)"),
    (47, 66, "Crinum — Náng vs Trinh nữ hoàng cung"),
    (30, 32, "Lamiaceae — Hoắc hương vs Hương nhu tía"),
    (43, 63, "Mạch môn vs Thiên môn đông (rễ củ giống)"),
    (53, 62, "Myrtaceae — Ổi vs Sim"),
]


def find_by_scientific(sci_name: str) -> Optional[Taxon]:
    """Khớp tên khoa học PlantNet → Taxon trong 70 loài (loài trước, rồi chi)."""
    if not sci_name:
        return None
    s = sci_name.strip().lower()
    # exact "genus species" prefix match
    for t in TAXA:
        binom = " ".join(t.sci.lower().split()[:2])
        if s.startswith(binom):
            return t
    # genus fallback
    genus = s.split()[0]
    group = _GENUS_INDEX.get(genus)
    if not group:
        return None
    if len(group) == 1:
        return group[0]
    parts = s.split()
    if len(parts) > 1:
        epi = parts[1]
        for t in group:
            if t.species_epithet.lower() == epi:
                return t
    return group[0]


def confusion_for(species_id: int) -> List[tuple]:
    out = []
    for a, b, note in CONFUSION_PAIRS:
        if species_id in (a, b):
            other = b if species_id == a else a
            out.append((other, BY_ID[other].vi, note))
    return out


def to_master_rows():
    """Trả về header + rows để xuất taxonomy_master.csv."""
    header = ["STT", "Tên Việt Nam", "Tên khoa học", "Họ thực vật",
              "Bộ phận dùng thuốc theo QĐ4664", "Tên đồng nghĩa (synonyms)",
              "Tên địa phương các vùng"]
    rows = [[t.id, t.vi, t.sci, t.family, t.organs_qd, t.synonyms, t.local] for t in TAXA]
    return header, rows


# Từ vựng bộ phận (P4)
ORGAN_TYPES = [
    ("leaf", "Lá"), ("stem", "Thân"), ("flower", "Hoa"), ("fruit", "Quả"),
    ("seed", "Hạt"), ("root", "Rễ"), ("rhizome", "Thân rễ"), ("bark", "Vỏ"),
    ("whole_plant", "Cả cây"), ("processed_herb", "Dược liệu (đã chế biến)"),
]
ORGAN_SUBTYPES = {
    "leaf": ["leaf_adaxial", "leaf_abaxial", "leaf_margin", "leaf_venation"],
    "flower": ["flower_front", "flower_side", "inflorescence"],
    "fruit": ["fruit_whole", "fruit_section"],
    "bark": ["bark_outer", "bark_section"],
    "root": ["root_whole", "root_section"],
    "rhizome": ["rhizome_whole", "rhizome_section"],
}

if __name__ == "__main__":
    assert len(TAXA) == 70, f"Phải đủ 70 loài, hiện {len(TAXA)}"
    print(f"OK — {len(TAXA)} loài. Ví dụ khớp PlantNet:")
    for q in ["Curcuma longa", "Zingiber officinale", "Mentha arvensis L.", "Rosa chinensis"]:
        t = find_by_scientific(q)
        print(f"  {q:28s} -> {t.vi if t else 'uncertain (ngoài danh mục)'}")
