# TODO: Automatisoitu työjono uusien sisältöjen hakemiseen, arviointiin ja esittämiseen

- Rakennetaan järjestelmä, joka hakee suuren määrän uusia postauksia, uutisia, videoita, tiedeartikkeleita jne.
    - Sisältöjen tulee olla uusia viime ajokertaan nähden (eli vain uudet sisällöt huomioidaan).
- Kielimalli arvioi jokaisen sisällön niiden "impactin" tai arvokkuuden perusteella suhteessa omaan profiiliisi.
    - Profiili voi sisältää kiinnostuksen kohteita, aiempia preferenssejä yms.
    - Malli tuottaa ranking-listan: mikä sisältö on arvokkainta, mikä vähiten.
- Uudet uutiset ja sisällöt esitetään web-sovelluksessa modernissa scrollattavassa näkymässä (vrt. Jodel, Reddit)
    - Käyttäjä voi selata sisältöjä helposti ja nopeasti.
    - Mahdollisuus merkitä kiinnostavat sisällöt talteen tai reagoida niihin.
- Työjono pyörii automaattisesti taustalla ja päivittyy säännöllisesti.

Tämä kokonaisuus automatisoi tiedonkeruun, arvioinnin ja esittämisen, ja tekee uusien merkityksellisten sisältöjen löytämisestä helppoa ja tehokasta.

# TODO: Lähteet Datainsinöörityöhön Keskittyviä Tietolähteitä

Seuraavaksi voisimme lisätä ja täydentää lähteitä, jotka ovat hyödyllisiä datainsinöörityöhön liittyen. Alla on alustava lista, jota voi täydentää jatkossa.

## 1. Blogit ja Verkkosivustot

- **Seattle Data Guy (Benjamin Rogojan):**
  - Blogi/Verkkosivusto: https://www.theseattledataguy.com/
  - YouTube: https://www.youtube.com/@SeattleDataGuy
  - Sisältöä: Paljon käytännönläheistä sisältöä datatekniikasta, datamallinnuksesta, ETL-prosesseista, SQL:stä ja uraneuvoja datainsinööreille. Hyvin arvostettu alalla.

- **Start Data Engineering (Andreas Kretz):**
  - Verkkosivusto: https://www.startdataengineering.com/
  - YouTube: https://www.youtube.com/@StartDataEngineering
  - Sisältöä: Kursseja, artikkeleita ja videoita, jotka kattavat datatekniikan perusteet ja edistyneemmät aiheet. Erityisen hyvä aloittelijoille ja uranvaihtajille.

- **Data Engineering Weekly:**
  - Uutiskirje/Verkkosivusto: https://www.dataengineeringweekly.com/
  - Sisältöä: Kuratoitu viikoittainen uutiskirje, joka kokoaa yhteen parhaat datatekniikkaan liittyvät artikkelit, työkalut ja uutiset. Erinomainen tapa pysyä ajan tasalla.

- **dbt Labs Blog:**
  - Blogi: https://www.getdbt.com/blog/
  - Sisältöä: Vaikka dbt on työkalu, heidän bloginsa käsittelee laajasti analytiikan suunnittelua (analytics engineering), datan muunnoksia, parhaita käytäntöjä ja modernia datastackia. Erittäin relevantti datainsinööreille.

- **Confluent Blog (Apache Kafka):**
  - Blogi: https://www.confluent.io/blog/
  - Sisältöä: Confluent on Apache Kafkan takana oleva yritys. Heidän bloginsa on johtava resurssi suoratoistodatan käsittelyyn, Kafkaan ja reaaliaikaisiin datarajapintoihin liittyen. Tärkeää monille moderneille data-arkkitehtuureille.

- **Airbyte Blog:**
  - Blogi: https://airbyte.com/blog
  - Sisältöä: Keskittyy datan integrointiin, ELT-prosesseihin ja avoimen lähdekoodin dataliittimiin. Hyödyllistä tietoa datan siirtämisestä ja yhdistämisestä eri lähteistä.

- **Zach Wilson's Blog:**
  - Blogi: https://zachwilson.tech/
  - Sisältöä: Käytännönläheisiä artikkeleita ja pohdintaa datatekniikasta, datan laadusta ja data-alustoista.

## 2. YouTube-kanavat (lisää)

- **Thu Vu data analytics:**
  - YouTube: https://www.youtube.com/@ThuvuDataAnalytics
  - Sisältöä: Keskittyy enemmän data-analytiikkaan, mutta sivuaa usein datatekniikan aiheita ja työkaluja, jotka ovat relevantteja myös insinööreille. Hyviä selityksiä konsepteista.

- **Andreas Kretz (Start Data Engineering):**
  - YouTube: https://www.youtube.com/@StartDataEngineering
  - (Mainittu jo blogien yhteydessä, mutta kanava on erinomainen itsessään)

## 3. Yhteisöt

- **DataTalks.Club:**
  - Verkkosivusto & Slack: https://datatalks.club/
  - Sisältöä: Aktiivinen yhteisö, jossa on kursseja (kuten heidän "Data Engineering Zoomcamp"), podcasteja, artikkeleita ja Slack-kanava keskusteluille. Hyvin käytännönläheinen ja yhteisöllinen.

- **r/dataengineering (Reddit):**
  - Reddit: https://www.reddit.com/r/dataengineering/
  - Sisältöä: Laaja ja aktiivinen yhteisö, jossa keskustellaan työkaluista, arkkitehtuureista, urakysymyksistä ja alan uutisista. Hyvä paikka esittää kysymyksiä ja oppia muilta.

- **Locally Optimistic:**
  - Slack & Blog: https://locallyoptimistic.com/
  - Sisältöä: Erityisesti analytiikan suunnitteluun (analytics engineering) ja moderniin datastackiin keskittyvä yhteisö ja blogi. Paljon keskustelua dbt:stä, Snowflakesta ja muista vastaavista työkaluista.

## 4. Podcastit

- **The Data Engineering Podcast:**
  - Sisältöä: Haastatteluja alan johtavien asiantuntijoiden kanssa datatekniikan eri osa-alueista, työkaluista ja trendeistä.

- **Data Engineering Show:**
  - Sisältöä: Keskusteluja ja näkemyksiä datatekniikan ammattilaisilta.

- **Monday Morning Data Chat:**
  - Sisältöä: Rennompi podcast, jossa käsitellään ajankohtaisia data-alan aiheita, usein datatekniikan näkökulmasta.

- **The Analytics Engineering Podcast (dbt Labs):**
  - Kuvaus: dbt Labsin isännöimä podcast, joka keskittyy analytiikan suunnitteluun (analytics engineering), moderniin datastackiin, dbt:hen ja siihen liittyviin teknologioihin ja käytäntöihin.
  - Löydät sen useimmilta podcast-alustoilta hakemalla nimellä "The Analytics Engineering Podcast" tai dbt Labsin verkkosivuilta.

