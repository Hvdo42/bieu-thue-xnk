# 📂 Biểu thuế XNK Việt Nam 2026

Công cụ tra cứu **Biểu thuế Xuất nhập khẩu Việt Nam 2026** — hoạt động **100% offline** trên trình duyệt, không cần cài đặt.

**👉 [Dùng ngay trên trình duyệt](https://hvdo42.github.io/bieu-thue-xnk/)**

---

## Tính năng

| Tab | Chức năng |
|-----|-----------|
| 🔍 **Tìm kiếm** | Nhập mã HS (vd: `7210`) hoặc tên hàng (vd: `thép cuộn`) → kết quả tức thì, hỗ trợ gõ không dấu |
| 📚 **Duyệt Chương** | Xem toàn bộ mã hàng theo 97 Chương của biểu thuế |
| 📖 **Chú thích** | Giải thích 25 ký hiệu thuế suất (FTA, TTĐB, BVMT…) và văn bản pháp quy |
| 💪 **Tính thuế** | Nhập nhiều mặt hàng, chọn loại thuế FTA, tính tổng thuế NK + VAT phải nộp |

## Dữ liệu

- **12,000 mã hàng**, 97 Chương
- **25 loại thuế suất:** NK thường, NK ưu đãi, VAT, EVFTA, CPTPP, UKVFTA, ATIGA, ACFTA, VKFTA, VN-EAEU, RCEP, AJCEP, VJEPA, AKFTA, AANZFTA, AIFTA, VCFTA, AHKFTA, VN-Cuba, VN-Lào, VN-Cam, VIFTA, TTĐB, Xuất khẩu, BVMT
- Cập nhật: **2026-04-05**

## Cách dùng

**Online:** Nhấn link ở trên.

**Offline (không cần mạng):** Chạy `python build.py` → mở `local/index.html`.

---

## Cấu trúc mã nguồn

| File | Mục đích |
|------|----------|
| `template.html` | App shell (HTML/CSS/JS) — chỉnh sửa tính năng ở đây |
| `app_data.json` | Dữ liệu 12.000 mã HS — cập nhật khi có biểu thuế mới |
| `build.py` | Build pipeline |
| `index.html` | Web build tự động (fetch data) — GitHub Pages serve file này |

```bash
python build.py        # → local/index.html  (standalone 6MB, mở file:// được)
python build.py --web  # → dist/index.html + dist/app_data.json
```

---

## ⚠️ Lưu ý

> Công cụ chỉ phục vụ **tra cứu nhanh và tham khảo cá nhân**.
> Không thay thế biểu thuế pháp lý chính thức của Bộ Tài chính.
> Luôn đối chiếu văn bản gốc trước khi khai báo hải quan.

---

*Tác giả: Võ Đỗ Hùng*
