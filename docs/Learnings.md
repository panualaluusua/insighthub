# Learnings from InsightHub Project

## 1. Tiedonkeruun automaatio ja API-rajapinnat
- Opin käyttämään Redditin ja YouTuben API-rajapintoja tehokkaasti.
- Pythonin requests-kirjasto ja Google API -client mahdollistivat monipuolisen tiedonkeruun.
- API-avainten hallinta .env-tiedostoissa ja ympäristömuuttujilla on tärkeää tietoturvan ja kehityksen kannalta.

## 2. Streamlit-käyttöliittymän rakentaminen
- Streamlit on nopea ja joustava tapa tehdä interaktiivisia datanäkymiä.
- Session state ja komponenttien välinen tiedonhallinta vaatii huolellista suunnittelua.
- Sivupalkin ja pääsisällön erottelu tekee käyttöliittymästä selkeän.

## 3. Käyttäjäkeskeinen suunnittelu ja oppimisen tukeminen
- Mindmap- ja tietomaisema-visualisoinnit auttavat käyttäjiä hahmottamaan osaamisensa ja tiedon aukkoja.
- LLM-pohjaiset promptit mahdollistavat podcast-muotoisten tiivistelmien personoinnin ja laadun parantamisen.
- Käyttäjän tavoitteiden ja kiinnostusten huomioiminen motivoi oppimista.

## 4. Monipuolinen sisällön käsittely ja yhdistely
- Reddit- ja YouTube-lähteiden yhdistäminen vaati yhtenäistä tietorakennetta ja yhteistä logiikkaa sisällön käsittelyyn.
- Sisältöjen automaattinen kategorisointi ja suodatus parantaa käyttökokemusta.
- Podcast-promptien esiasetukset ja muokattavuus tukevat erilaisia käyttötarpeita.

## 5. Projektinhallinta ja jatkokehitys
- Kehitysvaiheiden selkeä suunnittelu (feature roadmap, vision, backlog) auttaa pitämään projektin hallinnassa.
- Käyttäjäpalautteen keruu ja siihen reagoiminen on tärkeää jatkuvassa kehityksessä.
- Dokumentaatio (README, docs, mindmap, videot) tukee sekä omaa että muiden ymmärrystä projektista.

## 6. Haasteet ja ratkaisut
- API-rajapintojen rajoitukset ja autentikointi aiheuttivat päänvaivaa, mutta ratkesivat hyvällä virheenkäsittelyllä ja debuggausprinttien avulla.
- Selenium-automaatio osoittautui hitaaksi, joten siirryin Chrome-lisäosan käyttöön.
- Podcastien yksitoikkoisuus ratkesi prompttien ja rakenteen personoinnilla.

## 7. Yleisiä oppeja
- Ketterä kehitys ja iterointi: nopea prototypointi ja jatkuva parantaminen toimii parhaiten.
- Hyvä rakenne (src/, docs/, testit, ympäristömuuttujat) tekee projektista helposti ylläpidettävän.
- Dokumentointi ja näkyvä kehityshistoria auttavat sekä nykyistä että tulevaa kehitystä.

---

Tämä tiedosto kokoaa keskeiset opit InsightHub-projektin toteutuksesta, ja toimii muistilistana tuleviin projekteihin.
