from sqlalchemy import create_engine, MetaData, select, func, desc
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base


engine = create_engine("sqlite:///chinook.db", echo=False)


metadata = MetaData()
metadata.reflect(engine)


Base = automap_base(metadata=metadata)
Base.prepare()

Tracks = Base.classes.tracks
Albums = Base.classes.albums
InvoiceItems = Base.classes.invoice_items
Artists = Base.classes.artists

session = Session(engine)

# 1) Imprima os três primeiros registros da tabela tracks

print("=" * 70)
print("1) Três primeiros registros da tabela 'tracks':")
print("=" * 70)

stmt_1 = select(Tracks).limit(3)

for track in session.scalars(stmt_1):
    print(f"ID: {track.TrackId:<4} | Faixa: {track.Name:<35} | Preço: ${track.UnitPrice}")
print()

# 2) Imprima o nome da faixa e o título do álbum das primeiras 20 faixas

print("=" * 70)
print("2) Primeiras 20 faixas com o título de seus álbuns:")
print("=" * 70)

stmt_2 = (
    select(Tracks.Name, Albums.Title)
    .join(Albums, Tracks.AlbumId == Albums.AlbumId)
    .limit(20)
)

for track_name, album_title in session.execute(stmt_2):
    print(f"Faixa: {track_name:<35} | Álbum: {album_title}")
print()

# 3) Imprima as 10 primeiras vendas de faixas da tabela invoice_items

print("=" * 70)
print("3) Primeiras 10 vendas de faixas (invoice_items):")
print("=" * 70)

stmt_3 = select(InvoiceItems).limit(10)

for item in session.scalars(stmt_3):
    print(f"Item ID: {item.InvoiceLineId:<4} | Fatura: {item.InvoiceId:<4} | Track ID: {item.TrackId:<4} | Qtd: {item.Quantity} | Preço: ${item.UnitPrice}")
print()



# 4) Para essas 10 primeiras vendas, imprima os nomes das faixas e a quantidade

print("=" * 70)
print("4) Nomes das faixas e quantidades das 10 primeiras vendas:")
print("=" * 70)

stmt_4 = (
    select(Tracks.Name, InvoiceItems.Quantity)
    .join(Tracks, InvoiceItems.TrackId == Tracks.TrackId)
    .order_by(InvoiceItems.InvoiceLineId)
    .limit(10)
)

for track_name, quantity in session.execute(stmt_4):
    print(f"Faixa: {track_name:<40} | Quantidade: {quantity}")
print()



# 5) Imprima os nomes das 10 faixas mais vendidas e quantas vezes foram vendidas

print("=" * 70)
print("5) Top 10 faixas mais vendidas:")
print("=" * 70)

stmt_5 = (
    select(
        Tracks.Name,
        func.sum(InvoiceItems.Quantity).label("total_vendido")
    )
    .join(InvoiceItems, Tracks.TrackId == InvoiceItems.TrackId)
    .group_by(Tracks.TrackId, Tracks.Name)
    .order_by(desc("total_vendido"))
    .limit(10)
)

for track_name, total in session.execute(stmt_5):
    print(f"Faixa: {track_name:<45} | Vendas: {total}")
print()

# 6) Quem são os 10 artistas que mais venderam?

print("=" * 70)
print("6) Top 10 artistas com maior volume de vendas:")
print("=" * 70)

stmt_6 = (
    select(
        Artists.Name,
        func.sum(InvoiceItems.Quantity).label("total_vendido")
    )
    .join(Tracks, InvoiceItems.TrackId == Tracks.TrackId)
    .join(Albums, Tracks.AlbumId == Albums.AlbumId)
    .join(Artists, Albums.ArtistId == Artists.ArtistId)
    .group_by(Artists.ArtistId, Artists.Name)
    .order_by(desc("total_vendido"))
    .limit(10)
)

for artist_name, total in session.execute(stmt_6):
    print(f"Artista: {artist_name:<35} | Total de Faixas Vendidas: {total}")
print()

session.close()
