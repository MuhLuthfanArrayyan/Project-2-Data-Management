import random
import psycopg
from datetime import date, datetime, timedelta
from faker import Faker
from pathlib import Path

db_uri = "host=localhost port=5432 dbname=data_management user=postgres password=password"

generate = Faker('id_ID')
Faker.seed(42)
random.seed(42)

# Global memory caches untuk mempercepat penyusunan FK
produk_ids = []
unit_ids = []
kanal_ids = []
nasabah_ids = []
rekening_ids = []
rekening_aktif_ids = []  # Khusus menampung ID rekening berstatus AKTIF
kartu_map = {}           # {no_rekening: [no_kartu_1, ...]}
rekening_info_map = {}  # {no_rekening: {'saldo_efektif': ..., 'hold': ...}}

def create_tables(c):
    c.execute(Path(__file__).with_name('DDL.sql').read_text())

    print("selesai create table")

def backfill_produk_tabungan(c):
    global produk_ids
    produk_list = [
        ('PRD01', 'BritAma Umum', 'BRITAMA', 'UMUM', 'IDR', 50000.00, 'TIER', 12000.00, 'AKTIF'),
        ('PRD02', 'BritAma Bisnis', 'BRITAMA', 'MITRA', 'IDR', 100000.00, 'TIER', 20000.00, 'AKTIF'),
        ('PRD03', 'Simpedes Utama', 'SIMPEDES', 'UMUM', 'IDR', 25000.00, 'FLAT', 5500.00, 'AKTIF'),
        ('PRD04', 'Simpedes UMi', 'SIMPEDES', 'UMUM', 'IDR', 10000.00, 'FLAT', 0.00, 'AKTIF'),
        ('PRD05', 'BRI Junio', 'JUNIO', 'ANAK', 'IDR', 50000.00, 'FLAT', 5000.00, 'AKTIF'),
        ('PRD06', 'SimPel BRI', 'SIMPEL', 'PELAJAR', 'IDR', 5000.00, 'FLAT', 0.00, 'AKTIF'),
        ('PRD07', 'Tabungan Haji BRI', 'HAJI', 'UMUM', 'IDR', 500000.00, 'FLAT', 0.00, 'AKTIF'),
        ('PRD08', 'Tabunganku BRI', 'TABUNGANKU', 'UMUM', 'IDR', 20000.00, 'FLAT', 0.00, 'AKTIF'),
        ('PRD09', 'BritAma Valas', 'BRITAMA', 'PRIORITAS', 'USD', 100000.00, 'TIER', 25000.00, 'AKTIF'),
        ('PRD10', 'BritAma Muda', 'SIMUDA', 'PELAJAR', 'IDR', 50000.00, 'TIER', 10000.00, 'AKTIF')
    ]
    
    c.executemany("""
        INSERT INTO produk_tabungan (
            id_produk, nama_produk, keluarga_produk, segmen_tujuan, 
            mata_uang, saldo_minimum, skema_bunga, biaya_admin, status_produk
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, produk_list)
    
    produk_ids = [p[0] for p in produk_list]
    print("selesai backfill produk_tabungan")


def backfill_unit_kerja(c):
    global unit_ids
    units = [
        ('UK0001', 'Kantor Pusat BRI', 'HO', 'Jl. Jend. Sudirman No.44-46, Jakarta Pusat', None),
        ('UK0002', 'Kanwil BRI Jakarta 1', 'RO', 'Jl. Veteran No.8, Jakarta Pusat', 'UK0001'),
        ('UK0003', 'Kanwil BRI Bandung', 'RO', 'Jl. Asia Afrika No.51, Bandung', 'UK0001'),
        ('UK0004', 'Kanwil BRI Surabaya', 'RO', 'Jl. Jend. Basuki Rachmat No.122, Surabaya', 'UK0001'),
    ]
    
    for i in range(5, 51):
        uid = f"UK{i:04d}"
        jenis = random.choice(['CABANG', 'SUB_CABANG', 'UNIT', 'CASH_OFFICE', 'BRI_TERRACE'])
        induk = random.choice(['UK0002', 'UK0003', 'UK0004'])
        nama = f"BRI {jenis.title()} {generate.city()}"
        alamat = generate.address().replace('\n', ', ')[:140]
        units.append((uid, nama, jenis, alamat, induk))
        
    c.executemany("""
        INSERT INTO unit_kerja (id_unit_kerja, nama_unit_kerja, jenis_unit_kerja, alamat_lokasi, id_unit_induk)
        VALUES (%s, %s, %s, %s, %s)
    """, units)
    
    unit_ids = [u[0] for u in units]
    print("selesai backfill unit_kerja")


def backfill_kanal_layanan(c):
    global kanal_ids
    kanals = [
        ('KNL01', 'BRImo Super App', 'DIGITAL', 'ONLINE'),
        ('KNL02', 'Internet Banking BRI', 'DIGITAL', 'ONLINE'),
        ('KNL03', 'ATM / CRM BRI', 'SELF_SERVICE', 'ONLINE'),
        ('KNL04', 'Teller Kantor Cabang', 'TELLER_UNIT', 'ONLINE'),
        ('KNL05', 'AgenBRILink', 'AGENT', 'ONLINE'),
        ('KNL06', 'EDC Merchant BRI', 'MERCHANT', 'ONLINE'),
        ('KNL07', 'Kiosk Self Service', 'SELF_SERVICE', 'MAINTENANCE')
    ]
    
    c.executemany("""
        INSERT INTO kanal_layanan (id_kanal, nama_kanal, tipe_kanal, status_operasional)
        VALUES (%s, %s, %s, %s)
    """, kanals)
    
    kanal_ids = [k[0] for k in kanals]
    print("selesai backfill kanal_layanan")


def backfill_nasabah(c):
    global nasabah_ids
    total_nasabah = 10000
    batch_size = 2000
    used_niks = set()
    
    nasabah_data = []
    for i in range(1, total_nasabah + 1):
        nid = f"NSB{i:09d}"
        jenis = random.choices(['INDIVIDU', 'KORPORASI', 'LEMBAGA'], weights=[90, 7, 3])[0]
        
        if jenis == 'INDIVIDU':
            while True:
                nik = f"32{random.randint(1, 99):02d}{random.randint(1, 99):02d}{random.randint(1, 28):02d}{random.randint(1, 12):02d}{random.randint(50, 99):02d}{random.randint(1000, 9999)}"
                if nik not in used_niks:
                    used_niks.add(nik)
                    break
            nama = generate.name()
            segmen = random.choices(['MIKRO_UMI', 'RITEL', 'PRIORITAS', 'PRIVATE'], weights=[60, 30, 8, 2])[0]
        else:
            nik = f"NPWP{random.randint(100000000000, 999999999999)}"
            nama = generate.company()
            segmen = 'KORPORASI'
            
        status_kyc = random.choices(['TERVERIFIKASI', 'MENUNGGU_VERIFIKASI', 'PERLU_REKYC'], weights=[92, 5, 3])[0]
        tgl_reg = generate.date_between(start_date='-5y', end_date='today')
        
        nasabah_data.append((nid, nik, nama, jenis, segmen, status_kyc, tgl_reg))
        nasabah_ids.append(nid)
        
        if len(nasabah_data) >= batch_size:
            c.executemany("""
                INSERT INTO nasabah (id_nasabah, nik, nama_lengkap, jenis_nasabah, segmen_nasabah, status_kyc, tanggal_registrasi)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, nasabah_data)
            nasabah_data = []
            
    if nasabah_data:
        c.executemany("""
            INSERT INTO nasabah (id_nasabah, nik, nama_lengkap, jenis_nasabah, segmen_nasabah, status_kyc, tanggal_registrasi)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, nasabah_data)
        
    print("selesai backfill nasabah")


def backfill_rekening_tabungan(c):
    global rekening_ids, rekening_aktif_ids, rekening_info_map
    total_rekening = 12000
    batch_size = 2000
    
    rekening_data = []
    for i in range(1, total_rekening + 1):
        norek = f"002101{i:09d}"
        id_prd = random.choice(produk_ids)
        id_uk = random.choice(unit_ids)
        tgl_buka = generate.date_between(start_date='-4y', end_date='-1M')
        
        status_rek = random.choices(['AKTIF', 'DORMAN', 'TERBLOKIR', 'DITUTUP'], weights=[85, 8, 4, 3])[0]
        tgl_tutup = None
        hold = 0.00
        
        if status_rek == 'DITUTUP':
            tgl_tutup = generate.date_between(start_date=tgl_buka, end_date='today')
            saldo_efektif = 0.00
            saldo_tersedia = 0.00
        else:
            saldo_efektif = round(random.uniform(500000, 500000000), 2)
            hold = float(random.choice([0, 50000, 100000]))
            saldo_tersedia = max(0.00, round(saldo_efektif - hold, 2))
            
        rekening_data.append((norek, id_prd, 'IDR', tgl_buka, tgl_tutup, status_rek, saldo_efektif, saldo_tersedia, id_uk))
        rekening_ids.append(norek)
        
        # Pisahkan list rekening AKTIF agar transaksi hanya dibuat pada rekening AKTIF
        if status_rek == 'AKTIF':
            rekening_aktif_ids.append(norek)
            rekening_info_map[norek] = {
                'saldo_efektif': saldo_efektif,
                'hold': hold
            }
        
        if len(rekening_data) >= batch_size:
            c.executemany("""
                INSERT INTO rekening_tabungan (
                    no_rekening, id_produk, mata_uang, tanggal_buka, tanggal_tutup, 
                    status_rekening, saldo_efektif, saldo_tersedia, id_unit_kerja
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, rekening_data)
            rekening_data = []
            
    if rekening_data:
        c.executemany("""
            INSERT INTO rekening_tabungan (
                no_rekening, id_produk, mata_uang, tanggal_buka, tanggal_tutup, 
                status_rekening, saldo_efektif, saldo_tersedia, id_unit_kerja
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, rekening_data)
        
    print("selesai backfill rekening_tabungan")


def backfill_pemegang_rekening(c):
    pemegang_data = []
    
    # Pemegang utama diambil dari 90% nasabah pertama (10% sisanya tanpa rekening untuk Query R-05)
    active_nasabah_subset = nasabah_ids[:9000]
    
    for idx, norek in enumerate(rekening_ids):
        nid = active_nasabah_subset[idx % len(active_nasabah_subset)]
        pemegang_data.append((norek, nid, 'PEMEGANG_UTAMA', 'Y', generate.date_between(start_date='-4y', end_date='-1M')))
        
    joint_reks = random.sample(rekening_ids, 800)
    for norek in joint_reks:
        nid = random.choice(active_nasabah_subset)
        pemegang_data.append((norek, nid, 'PESERTA', 'N', generate.date_between(start_date='-3y', end_date='-1M')))
        
    unique_pemegang = list({(p[0], p[1]): p for p in pemegang_data}.values())
    
    c.executemany("""
        INSERT INTO pemegang_rekening (no_rekening, id_nasabah, peran, penanda_utama, tanggal_mulai)
        VALUES (%s, %s, %s, %s, %s)
    """, unique_pemegang)
    
    print("selesai backfill pemegang_rekening")


def backfill_kartu_debit(c):
    global kartu_map
    kartu_data = []
    today = date.today()
    
    # POIN 1 REVISI: Hanya buat kartu debit untuk rekening yang berstatus AKTIF
    for idx, norek in enumerate(rekening_aktif_ids):
        if random.random() < 0.8:
            nokartu = f"522184{idx+1:010d}"
            bentuk = random.choice(['FISIK', 'VIRTUAL'])
            jaringan = random.choice(['MASTERCARD', 'VISA', 'GPN_PRIVATE_LABEL'])
            status = random.choices(['AKTIF', 'BLOKIR_SEMENTARA', 'KEDALUWARSA'], weights=[90, 5, 5])[0]
            
            # 10% kartu mendekati tanggal kadaluarsa (1-29 hari ke depan) untuk Query R-09
            if random.random() < 0.10:
                tgl_exp = generate.date_between(start_date=today + timedelta(days=1), end_date=today + timedelta(days=29))
                tgl_terbit = tgl_exp - timedelta(days=5*365)
            else:
                tgl_terbit = generate.date_between(start_date='-5y', end_date='-1M')
                tgl_exp = tgl_terbit + timedelta(days=5*365)
            
            kartu_data.append((nokartu, norek, bentuk, jaringan, status, tgl_terbit, tgl_exp))
            
            if norek not in kartu_map:
                kartu_map[norek] = []
            kartu_map[norek].append(nokartu)
            
    c.executemany("""
        INSERT INTO kartu_debit (
            no_kartu, no_rekening, bentuk_kartu, jaringan_kartu, 
            status_kartu, tanggal_terbit, tanggal_kadaluarsa
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, kartu_data)
    
    print("selesai backfill kartu_debit")


def backfill_transaksi_tabungan(c):
    transaksi_data = []
    rekening_updates = []
    batch_size = 5000
    tx_count = 1
    total_tx_inserted = 0
    
    reks_with_cards = list(kartu_map.keys())
    
    for norek in reks_with_cards:
        num_tx = random.randint(40, 80)
        info = rekening_info_map[norek]
        running_saldo = info['saldo_efektif']
        hold_amount = info['hold']
        
        timestamps = sorted([generate.date_time_between(start_date='-1y', end_date='now') for _ in range(num_tx)])
        
        for waktu in timestamps:
            tx_id = f"TX2026{tx_count:012d}"
            tx_count += 1
            
            jenis = random.choice(['SETORAN', 'PENARIKAN', 'TRANSFER', 'PEMBAYARAN', 'BIAYA'])
            arah = 'KREDIT' if jenis == 'SETORAN' else 'DEBIT'
            nominal = round(random.uniform(50000, 2000000), 2)
            id_knl = random.choice(kanal_ids)
            nokartu = random.choice(kartu_map[norek])
            
            if arah == 'DEBIT' and nominal > running_saldo:
                status = 'GAGAL'
                saldo_setelah = None
            else:
                status = random.choices(['BERHASIL', 'GAGAL', 'PENDING'], weights=[94, 5, 1])[0]
                if status == 'BERHASIL':
                    if arah == 'KREDIT':
                        running_saldo += nominal
                    else:
                        running_saldo -= nominal
                    saldo_setelah = round(running_saldo, 2)
                else:
                    saldo_setelah = None
            
            transaksi_data.append((
                tx_id, norek, jenis, arah, nominal, 'IDR', 
                waktu, id_knl, nokartu, status, saldo_setelah
            ))
            total_tx_inserted += 1
            
            if len(transaksi_data) >= batch_size:
                c.executemany("""
                    INSERT INTO transaksi_tabungan (
                        id_transaksi, no_rekening, jenis_transaksi, arah, nominal, 
                        mata_uang, waktu_transaksi, id_kanal, no_kartu, status_transaksi, saldo_setelah
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, transaksi_data)
                transaksi_data = []

        # POIN 2 REVISI: Catat saldo akhir hasil kalkulasi transaksi untuk di-UPDATE balik ke rekening_tabungan
        final_efektif = round(running_saldo, 2)
        final_tersedia = max(0.00, round(final_efektif - hold_amount, 2))
        rekening_updates.append((final_efektif, final_tersedia, norek))
                
    if transaksi_data:
        c.executemany("""
            INSERT INTO transaksi_tabungan (
                id_transaksi, no_rekening, jenis_transaksi, arah, nominal, 
                mata_uang, waktu_transaksi, id_kanal, no_kartu, status_transaksi, saldo_setelah
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, transaksi_data)

    # POIN 2 REVISI: Update saldo_efektif & saldo_tersedia pada tabel rekening_tabungan
    if rekening_updates:
        c.executemany("""
            UPDATE rekening_tabungan 
            SET saldo_efektif = %s, saldo_tersedia = %s 
            WHERE no_rekening = %s
        """, rekening_updates)
        
    print(f"selesai backfill transaksi_tabungan (Total: {total_tx_inserted:,} record)")
    return total_tx_inserted


def backfill_posting_bunga(c):
    posting_data = []
    periodes = ['202607', '202608', '202609', '202610']
    
    # Hanya posting bunga pada rekening berstatus AKTIF
    for norek in random.sample(rekening_aktif_ids, min(5000, len(rekening_aktif_ids))):
        for prd in periodes:
            hari = random.randint(28, 31)
            tarif = 0.0150
            b_kotor = round(random.uniform(5000, 150000), 2)
            pajak = round(b_kotor * 0.20, 2)
            b_bersih = round(b_kotor - pajak, 2)
            tgl_post = datetime.strptime(f"{prd}25 23:59:59", "%Y%m%d %H:%M:%S")
            
            posting_data.append((norek, prd, hari, tarif, b_kotor, pajak, b_bersih, tgl_post))
            
    c.executemany("""
        INSERT INTO posting_bunga (
            no_rekening, periode, hari_berjalan, tarif_bunga, 
            bunga_kotor, pajak_pph_final, bunga_bersih, tanggal_posting
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, posting_data)
    
    print("selesai backfill posting_bunga")


def backfill_instruksi_terjadwal(c):
    instruksi_data = []
    
    for i in range(1, 1501):
        id_inst = f"INS{i:012d}"
        jenis = random.choice(['AFT', 'AUTODEBET', 'AGF', 'ACCOUNT_SWEEP'])
        sumber = random.choice(rekening_aktif_ids)
        
        tujuan = None
        if jenis in ['AFT', 'ACCOUNT_SWEEP']:
            while True:
                tujuan = random.choice(rekening_aktif_ids)
                if tujuan != sumber:
                    break
                    
        frekuensi = random.choice(['HARIAN', 'MINGGUAN', 'BULANAN'])
        
        if frekuensi == 'HARIAN':
            hari_eksekusi = None
        elif frekuensi == 'MINGGUAN':
            hari_eksekusi = random.randint(1, 7)
        else:
            hari_eksekusi = random.randint(1, 28)
            
        nominal = round(random.uniform(100000, 2000000), 2) if jenis == 'AFT' else round(random.uniform(50000, 1000000), 2)
        status = random.choices(['AKTIF', 'DITANGGUHKAN', 'BERAKHIR'], weights=[85, 10, 5])[0]
        
        tgl_mulai = generate.date_between(start_date='-1y', end_date='today')
        tgl_selesai = tgl_mulai + timedelta(days=365) if status == 'BERAKHIR' else None
        
        instruksi_data.append((
            id_inst, jenis, sumber, tujuan, frekuensi, 
            hari_eksekusi, nominal, status, tgl_mulai, tgl_selesai
        ))
        
    c.executemany("""
        INSERT INTO instruksi_terjadwal (
            id_instruksi, jenis_instruksi, no_rekening_sumber, no_rekening_tujuan, 
            frekuensi, hari_eksekusi, nominal_target, status_instruksi, tanggal_mulai, tanggal_selesai
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, instruksi_data)
    
    print("selesai backfill instruksi_terjadwal")


if __name__ == "__main__":
    with psycopg.connect(db_uri) as conn:
        with conn.cursor() as c:
            create_tables(c)
            
            c.execute("SELECT count(*) FROM nasabah")
            if c.fetchone()[0] > 0:
                raise SystemExit("sudah pernah backfill")

            print("Memulai proses seeding data...")
            backfill_produk_tabungan(c)
            backfill_unit_kerja(c)
            backfill_kanal_layanan(c)
            backfill_nasabah(c)
            backfill_rekening_tabungan(c)
            backfill_pemegang_rekening(c)
            backfill_kartu_debit(c)
            total_tx = backfill_transaksi_tabungan(c)
            backfill_posting_bunga(c)
            backfill_instruksi_terjadwal(c)
            
            conn.commit()
            # POIN 3 REVISI: Teks label telah dibersihkan
            print(f"Seeding 10.000 Nasabah & {total_tx:,} Transaksi BERHASIL diselesaikan!")
