-- DDL disalin dari laporan "Project Part-2 Report.pdf" Bab 2.2
-- Urutan dibuat parent -> child supaya FOREIGN KEY tidak error

CREATE TABLE produk_tabungan (
    id_produk VARCHAR(10) PRIMARY KEY,
    nama_produk VARCHAR(50) NOT NULL UNIQUE,
    keluarga_produk VARCHAR(12) NOT NULL,
    segmen_tujuan VARCHAR(20) NOT NULL,
    mata_uang VARCHAR(60) NOT NULL DEFAULT 'IDR',
    saldo_minimum NUMERIC(18,2) NOT NULL DEFAULT 0,
    skema_bunga VARCHAR(10) NOT NULL,
    biaya_admin NUMERIC(18,2) NOT NULL DEFAULT 0,
    status_produk VARCHAR(15) NOT NULL DEFAULT 'AKTIF',

    CONSTRAINT chk_produk_keluarga CHECK (keluarga_produk IN ('BRITAMA','JUNIO','SIMUDA','HAJI','SIMPEDES','SIMPEL','TABUNGANKU')),
    CONSTRAINT chk_produk_segmen CHECK (segmen_tujuan IN ('UMUM','ANAK','PELAJAR','TKI','MITRA','PRIORITAS','DHE')),
    CONSTRAINT chk_produk_skema_bunga CHECK (skema_bunga IN ('FLAT','TIER')),
    CONSTRAINT chk_produk_status CHECK (status_produk IN ('AKTIF','TIDAK_DIPASARKAN')),
    CONSTRAINT chk_produk_saldo_minimum CHECK (saldo_minimum >= 0),
    CONSTRAINT chk_produk_biaya_admin CHECK (biaya_admin >= 0)
);

CREATE TABLE unit_kerja (
    id_unit_kerja VARCHAR(10) PRIMARY KEY,
    nama_unit_kerja VARCHAR(60) NOT NULL,
    jenis_unit_kerja VARCHAR(15) NOT NULL,
    alamat_lokasi VARCHAR(150) NOT NULL,
    id_unit_induk VARCHAR(10),

    FOREIGN KEY (id_unit_induk) REFERENCES unit_kerja (id_unit_kerja),

    CONSTRAINT chk_unit_kerja_jenis CHECK (jenis_unit_kerja IN ('HO','RO','CABANG','SUB_CABANG','UNIT','CASH_OFFICE','BRI_TERRACE')),
    CONSTRAINT chk_unit_kerja_induk_beda CHECK (id_unit_induk IS NULL OR id_unit_induk <> id_unit_kerja)
);

CREATE TABLE kanal_layanan (
    id_kanal VARCHAR(10) PRIMARY KEY,
    nama_kanal VARCHAR(30) NOT NULL UNIQUE,
    tipe_kanal VARCHAR(15) NOT NULL,
    status_operasional VARCHAR(12) NOT NULL,

    CONSTRAINT chk_kanal_tipe CHECK (tipe_kanal IN ('DIGITAL','SELF_SERVICE','TELLER_UNIT','AGENT','MERCHANT')),
    CONSTRAINT chk_kanal_status CHECK (status_operasional IN ('ONLINE','OFFLINE','MAINTENANCE'))
);

CREATE TABLE nasabah (
    id_nasabah VARCHAR(12) PRIMARY KEY,
    nik VARCHAR(20) NOT NULL UNIQUE,
    nama_lengkap VARCHAR(100) NOT NULL,
    jenis_nasabah VARCHAR(12) NOT NULL,
    segmen_nasabah VARCHAR(12) NOT NULL,
    status_kyc VARCHAR(20) NOT NULL DEFAULT 'BELUM_VERIFIKASI',
    tanggal_registrasi DATE NOT NULL DEFAULT CURRENT_DATE,

    CONSTRAINT chk_nasabah_jenis CHECK (jenis_nasabah IN ('INDIVIDU','KORPORASI','LEMBAGA')),
    CONSTRAINT chk_nasabah_segmen CHECK (segmen_nasabah IN ('MIKRO_UMI','RITEL','KORPORASI','PRIORITAS','PRIVATE')),
    CONSTRAINT chk_nasabah_status_kyc CHECK (status_kyc IN ('TERVERIFIKASI','MENUNGGU_VERIFIKASI','DITOLAK','PERLU_REKYC')),
    CONSTRAINT chk_nasabah_tanggal_registrasi CHECK (tanggal_registrasi <= CURRENT_DATE),
    CONSTRAINT chk_nasabah_nik_individu CHECK (jenis_nasabah <> 'INDIVIDU' OR nik ~ '^[0-9]{16}$')
);

CREATE TABLE rekening_tabungan (
    no_rekening VARCHAR(15) PRIMARY KEY,
    id_produk VARCHAR(10) NOT NULL,
    mata_uang CHAR(3) NOT NULL DEFAULT 'IDR',
    tanggal_buka DATE NOT NULL DEFAULT CURRENT_DATE,
    tanggal_tutup DATE,
    status_rekening VARCHAR(12) NOT NULL DEFAULT 'AKTIF',
    saldo_efektif NUMERIC(18,2) NOT NULL DEFAULT 0,
    saldo_tersedia NUMERIC(18,2) NOT NULL DEFAULT 0,
    id_unit_kerja VARCHAR(10),

    FOREIGN KEY (id_produk) REFERENCES produk_tabungan (id_produk),
    FOREIGN KEY (id_unit_kerja) REFERENCES unit_kerja (id_unit_kerja),

    CONSTRAINT chk_rekening_status CHECK (status_rekening IN ('AKTIF','DORMAN','TERBLOKIR','DITUTUP')),
    CONSTRAINT chk_rekening_tanggal_buka CHECK (tanggal_buka <= CURRENT_DATE),
    CONSTRAINT chk_rekening_tanggal_tutup CHECK (tanggal_tutup IS NULL OR tanggal_tutup >= tanggal_buka),
    CONSTRAINT chk_rekening_tutup_wajib_tanggal CHECK (status_rekening <> 'DITUTUP' OR tanggal_tutup IS NOT NULL),
    CONSTRAINT chk_rekening_saldo_efektif CHECK (saldo_efektif >= 0),
    CONSTRAINT chk_rekening_saldo_tersedia CHECK (saldo_tersedia >= 0 AND saldo_tersedia <= saldo_efektif)
);

CREATE TABLE pemegang_rekening (
    no_rekening VARCHAR(15) NOT NULL,
    id_nasabah VARCHAR(12) NOT NULL,
    peran VARCHAR(15) NOT NULL,
    penanda_utama CHAR(1) NOT NULL,
    tanggal_mulai DATE NOT NULL DEFAULT CURRENT_DATE,

    PRIMARY KEY (no_rekening, id_nasabah),
    FOREIGN KEY (no_rekening) REFERENCES rekening_tabungan (no_rekening),
    FOREIGN KEY (id_nasabah) REFERENCES nasabah (id_nasabah),

    CONSTRAINT chk_pemegang_peran CHECK (peran IN ('PEMEGANG_UTAMA','PESERTA','PEMBERI_KUASA')),
    CONSTRAINT chk_pemegang_penanda_utama CHECK (penanda_utama IN ('Y','N'))
);

CREATE TABLE kartu_debit (
    no_kartu VARCHAR(19) PRIMARY KEY,
    no_rekening VARCHAR(15) NOT NULL,
    bentuk_kartu VARCHAR(8) NOT NULL,
    jaringan_kartu VARCHAR(20) NOT NULL, -- revisi: VARCHAR(15) tidak muat 'GPN_PRIVATE_LABEL' (17 karakter)
    status_kartu VARCHAR(18) NOT NULL DEFAULT 'BELUM_AKTIF',
    tanggal_terbit DATE NOT NULL,
    tanggal_kadaluarsa DATE NOT NULL,

    FOREIGN KEY (no_rekening) REFERENCES rekening_tabungan (no_rekening),

    CONSTRAINT chk_kartu_bentuk CHECK (bentuk_kartu IN ('FISIK','VIRTUAL')),
    CONSTRAINT chk_kartu_jaringan CHECK (jaringan_kartu IN ('MASTERCARD','VISA','GPN_PRIVATE_LABEL')),
    CONSTRAINT chk_kartu_status CHECK (status_kartu IN ('AKTIF','BLOKIR_SEMENTARA','BLOKIR_PERMANEN','KEDALUWARSA')),
    CONSTRAINT chk_kartu_tanggal CHECK (tanggal_kadaluarsa > tanggal_terbit)
);

CREATE TABLE transaksi_tabungan (
    id_transaksi VARCHAR(20) PRIMARY KEY,
    no_rekening VARCHAR(15) NOT NULL,
    jenis_transaksi VARCHAR(12) NOT NULL,
    arah VARCHAR(6) NOT NULL,
    nominal NUMERIC(18,2) NOT NULL,
    mata_uang CHAR(3) NOT NULL,
    waktu_transaksi TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_kanal VARCHAR(10) NOT NULL,
    no_kartu VARCHAR(19) NOT NULL,
    status_transaksi VARCHAR(10) NOT NULL,
    saldo_setelah NUMERIC(18,2),

    FOREIGN KEY (no_rekening) REFERENCES rekening_tabungan (no_rekening),
    FOREIGN KEY (id_kanal) REFERENCES kanal_layanan (id_kanal),
    FOREIGN KEY (no_kartu) REFERENCES kartu_debit (no_kartu),

    CONSTRAINT chk_transaksi_jenis CHECK (jenis_transaksi IN ('SETORAN','PENARIKAN','TRANSFER','PEMBAYARAN','BIAYA','REVERSAL')),
    CONSTRAINT chk_transaksi_arah CHECK (arah IN ('KREDIT','DEBIT')),
    CONSTRAINT chk_transaksi_nominal CHECK (nominal > 0),
    CONSTRAINT chk_transaksi_status CHECK (status_transaksi IN ('BERHASIL','GAGAL','PENDING','REVERSED')),
    CONSTRAINT chk_transaksi_saldo_setelah_wajib CHECK (status_transaksi <> 'BERHASIL' OR saldo_setelah IS NOT NULL)
);

CREATE TABLE posting_bunga (
    no_rekening VARCHAR(15) NOT NULL,
    periode CHAR(6) NOT NULL,
    hari_berjalan INTEGER NOT NULL,
    tarif_bunga NUMERIC(5,4) NOT NULL DEFAULT 0,
    bunga_kotor NUMERIC(18,2) NOT NULL DEFAULT 0,
    pajak_pph_final NUMERIC(18,2) NOT NULL DEFAULT 0,
    bunga_bersih NUMERIC(18,2) NOT NULL,
    tanggal_posting TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (no_rekening, periode),
    FOREIGN KEY (no_rekening) REFERENCES rekening_tabungan (no_rekening),

    CONSTRAINT chk_posting_bunga_periode CHECK (periode ~ '^[0-9]{4}(0[1-9]|1[0-2])$'),
    CONSTRAINT chk_posting_bunga_hari CHECK (hari_berjalan BETWEEN 1 AND 366),
    CONSTRAINT chk_posting_bunga_tarif CHECK (tarif_bunga > 0),
    CONSTRAINT chk_posting_bunga_kotor CHECK (bunga_kotor >= 0),
    CONSTRAINT chk_posting_bunga_pajak CHECK (pajak_pph_final >= 0),
    CONSTRAINT chk_posting_bunga_bersih CHECK (bunga_bersih = bunga_kotor - pajak_pph_final),
    CONSTRAINT chk_posting_bunga_tanggal CHECK (TO_CHAR(tanggal_posting, 'YYYYMM') = periode)
);

CREATE TABLE instruksi_terjadwal (
    id_instruksi VARCHAR(15) PRIMARY KEY,
    jenis_instruksi VARCHAR(15) NOT NULL,
    no_rekening_sumber VARCHAR(15) NOT NULL,
    no_rekening_tujuan VARCHAR(15),
    frekuensi VARCHAR(15) NOT NULL,
    hari_eksekusi INTEGER, -- revisi: NOT NULL dihapus supaya frekuensi HARIAN (hari_eksekusi NULL) bisa di-insert
    nominal_target NUMERIC(18,2),
    status_instruksi VARCHAR(12) NOT NULL DEFAULT 'AKTIF',
    tanggal_mulai DATE NOT NULL,
    tanggal_selesai DATE,

    FOREIGN KEY (no_rekening_sumber) REFERENCES rekening_tabungan (no_rekening),
    FOREIGN KEY (no_rekening_tujuan) REFERENCES rekening_tabungan (no_rekening),

    CONSTRAINT chk_instruksi_jenis CHECK (jenis_instruksi IN ('AFT','AUTODEBET','AGF','ACCOUNT_SWEEP','NAS')),
    CONSTRAINT chk_instruksi_frekuensi CHECK (frekuensi IN ('HARIAN','MINGGUAN','BULANAN')),
    CONSTRAINT chk_instruksi_status CHECK (status_instruksi IN ('AKTIF','DITANGGUHKAN','BERAKHIR')),
    CONSTRAINT chk_instruksi_hari_eksekusi CHECK (
        (frekuensi = 'HARIAN'   AND hari_eksekusi IS NULL) OR
        (frekuensi = 'MINGGUAN' AND hari_eksekusi BETWEEN 1 AND 7) OR
        (frekuensi = 'BULANAN'  AND hari_eksekusi BETWEEN 1 AND 31)
    ),
    CONSTRAINT chk_instruksi_nominal_target CHECK (nominal_target IS NULL OR nominal_target > 0),
    CONSTRAINT chk_instruksi_nominal_wajib_aft CHECK (jenis_instruksi <> 'AFT' OR nominal_target IS NOT NULL),
    CONSTRAINT chk_instruksi_tujuan_beda_sumber CHECK (no_rekening_tujuan IS NULL OR no_rekening_tujuan <> no_rekening_sumber),
    CONSTRAINT chk_instruksi_tujuan_wajib CHECK (jenis_instruksi NOT IN ('AFT','ACCOUNT_SWEEP') OR no_rekening_tujuan IS NOT NULL),
    CONSTRAINT chk_instruksi_tanggal_selesai CHECK (tanggal_selesai IS NULL OR tanggal_selesai >= tanggal_mulai)
);
