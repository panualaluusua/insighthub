# Product Requirements Document (PRD)
## Automatisoitu työjono uusien sisältöjen hakemiseen, arviointiin ja esittämiseen

### 1. Tausta ja tavoite
Tavoitteena on rakentaa järjestelmä, joka automatisoi uusien tietolähteiden (uutiset, postaukset, videot, tiedeartikkelit jne.) keruun, arvioinnin ja esittämisen käyttäjän henkilökohtaisen profiilin perusteella. Lopputuloksena käyttäjä saa scrollattavan näkymän, jossa hänelle merkityksellisimmät sisällöt ovat helposti löydettävissä ja selattavissa.

### 2. Ominaisuudet

#### 2.x Sisällön täydellinen lataus LLM-arviointia varten
- Reddit-postauksista haetaan koko tekstisisältö (otsikko, selftext, mahdolliset kommentit tarpeen mukaan).
    - YouTube-videoista haetaan metadatan lisäksi myös transkripti (tekstitys). Nyt käytössä on kaksi transkriptiomenetelmää:
        - **OpenAI Whisper API:** Ensisijainen ja suositeltu menetelmä korkealaatuisten transkriptioiden saamiseksi. Äänitiedostoja esikäsitellään FFmpegillä nopeuttamalla niitä, mikä vähentää transkriptioon kuluvaa aikaa ja API-kustannuksia.
        - **Faster-Whisper (paikallinen):** Vararatkaisuna tai paikalliseen käyttöön, jos OpenAI API ei ole käytettävissä tai halutaan välttää API-kustannuksia.
        - Jos transkriptiota ei voida tuottaa kummallakaan menetelmällä, LLM-arviointi rajoittuu metatietoihin (otsikko, kuvaus).
- Tämä mahdollistaa sisällön syvällisen arvioinnin kielimallilla, eikä pelkän metadatan perusteella.
#### 2.1 Sisällön keruu
- Järjestelmä hakee suuren määrän uusia sisältöjä useista lähteistä (esim. uutis- ja videosivustot, tieteelliset julkaisut, some).
- Vain sellaiset sisällöt huomioidaan, jotka ovat uusia viime ajokertaan nähden.
- Lähteet ja hakutiheys voidaan määrittää konfiguroitavasti.

#### 2.2 Arviointi ja ranking
- Arviointi toteutetaan monivaiheisena prosessina, erityisesti pitkien sisältöjen (esim. YouTube-videot) kohdalla:
    1. Ensin tiivistetään sisältö, jos se on pitkä (esim. transkriptin summarointi).
    2. Tämän jälkeen arvioidaan tiivistelmän ja käyttäjäprofiilin pohjalta sisällön arvo ja relevanssi käyttäjälle.
    3. Tarvittaessa LLM:ltä voidaan pyytää myös perusteluja/arvioinnin selitystä (esim. miksi sisältö on hyödyllinen?).
- Tämä monivaiheinen työjono parantaa erityisesti pitkien sisältöjen arvioinnin laatua ja varmistaa, että ranking on mahdollisimman osuva käyttäjän näkökulmasta.
- Profiili koostuu mm. kiinnostuksen kohteista, aiemmista valinnoista ja mahdollisista käyttäjän antamista painotuksista.
- Jokaiselle sisällölle lasketaan "arvokkuus-score" ja sisällöt järjestetään tämän perusteella.

#### 2.3 Esitystapa
- Sisällöt esitetään web-sovelluksessa modernissa, helposti scrollattavassa näkymässä (vrt. Jodel, Reddit).
- Käyttäjä voi selata, tallentaa ja reagoida sisältöihin (esim. tykkäys, tallenna, piilota).
- Käyttöliittymä on responsiivinen ja mobiiliystävällinen.

#### 2.4 Automaatio ja päivitys
- Työjono toimii automaattisesti taustalla ja päivittyy säännöllisesti.
- Käyttäjälle voidaan ilmoittaa uusista merkityksellisistä sisällöistä.

### 3. Rajaukset
- Ensimmäisessä versiossa keskitytään vain muutamaan sisältölähteeseen.
- Kielimallin arviointi voi perustua valmiisiin API:hin tai omiin malleihin.
- Käyttäjän profiili voidaan aluksi rakentaa yksinkertaisilla kysymyksillä/interaktioilla.

### 4. MVP (Minimum Viable Product)
- Sisältöjen haku yhdestä tai kahdesta lähteestä
- Yksinkertainen ranking käyttäjän kiinnostuksen kohteiden perusteella
- Scrollattava lista web-sovelluksessa
- Perustoiminnot: selaus, tykkäys, tallenna

### 5. Jatkokehitysideoita
- Lisää sisältölähteitä ja monipuolisempi profiilointi
- Kehittyneempi ranking ja personointi
- Push-ilmoitukset ja aktiivinen tiedon tarjoaminen
- Yhteisölliset ominaisuudet (kommentointi, jakaminen)

---

### 6. Toimintalogiikan kaavio (Mermaid)

```mermaid
flowchart TD
    A[Reddit & YouTube URL-haku] --> B[Sisällön lataus (otsikko, teksti, videoiden kuvaukset)]
    B --> C[LLM-arviointi (arvokkuus, relevanssi)]
    C --> D[Ranking & järjestys käyttäjäprofiilin mukaan]
    D --> E[Scrollattava UI: lista ja interaktiot]
    E -->|Tykkäys/tallennus/piilotus| F[Päivitys käyttäjäprofiiliin]
    F -.-> C
```

- Vaihe A: Haetaan Reddit- ja YouTube-urlit (toteutettu)
- Vaihe B: Ladataan varsinainen sisältö (esim. postauksen teksti, YouTube-kuvaus)
- Vaihe C: Arvioidaan LLM:llä sisällön arvokkuus ja relevanssi käyttäjälle
- Vaihe D: Järjestetään sisällöt ranking-listaksi profiilin perusteella
- Vaihe E: Esitetään sisällöt scrollattavassa käyttöliittymässä, jossa käyttäjä voi reagoida
- Vaihe F: Käyttäjän interaktiot päivittävät profiilia ja vaikuttavat jatkossa ranking-arvioihin

Tämä PRD toimii pohjana kehitystyölle ja sitä voidaan täydentää projektin edetessä.


# Teknologiasuunnitelma

Tämä teknologiasuunnitelma perustuu "Nopea Prototyyppi / Low-Code" -lähestymistapaan, jonka tavoitteena on mahdollistaa nopea kehitys, iterointi ja tuotantoon siirtyminen mahdollisimman vähällä koodilla ja ylläpidolla.

---

## Vaihe 1: Perustan luominen – Supabase

**Miksi Supabase?**
- Tarjoaa PostgreSQL-tietokannan, REST- ja GraphQL-rajapinnat sekä autentikaation ja Edge Functions -toiminnot yhdessä paketissa.
- pgvector-laajennus mahdollistaa vektoriupotusten tallentamisen ja vertailun (personointi, sisältöjen ranking).
- Skaalautuu hyvin tuotantoon ja tukee jatkokehitystä.

**Toimenpiteet:**
1. Luo Supabase-projekti osoitteessa [supabase.com](https://supabase.com).
2. Suunnittele tietokantataulut:
    - **content**: id (PK), created_at, source, url, title, full_text, metadata (JSONB), embedding (vector)
    - **profiles**: id (viittaa auth.users), updated_at, interest_vector (vector)
    - **interactions**: id, user_id, content_id, interaction_type (esim. 'like', 'save', 'hide')
3. Aktivoi pgvector-laajennus (Database → Extensions → vector).

> **Lopputulos:** Toimiva tietokanta ja API, johon voit tallentaa ja josta voit hakea dataa.

---

## Vaihe 2: Automaattinen sisällönkeruu ja -arviointi – n8n

**Miksi n8n?**
- Visuaalinen työnkulkujen rakentaja, joka nopeuttaa integraatioiden ja automaatioiden toteutusta ilman palvelinkoodia.
- Helppo ylläpitää ja laajentaa, soveltuu hyvin prototyyppiin ja tuotantoon.

**Toimenpiteet:**
1. Pystytä n8n (pilviversio tai Docker).
2. Rakenna työnkulku:
    - **Ajastus**: Schedule node (esim. 1h välein)
    - **Sisällön haku**: HTTP Request node (Reddit JSON API, YouTube API)
    - **Uutuustarkistus**: Tarkista Supabasesta, onko sisältö jo olemassa
    - **Koko sisällön lataus**: Hae Redditin tekstisisältö tai YouTube-transkripti (tarvittaessa esim. youtube-transcript-kirjastolla)
    - **LLM-arviointi ja upotus**: OpenAI/Mistral AI -node, promptilla "Analysoi ja luo upotusvektori"
    - **Tallennus**: Insert Supabaseen (content-taulu)

> **Lopputulos:** Automatisoitu prosessi, joka kerää, arvioi ja tallentaa uutta sisältöä tietokantaan säännöllisesti.

---

## Vaihe 3: Käyttöliittymä – SvelteKit

**Miksi SvelteKit?**
- Moderni, kevyt ja nopea framework responsiivisen web-sovelluksen rakentamiseen.
- Helppo yhdistää Supabaseen ja mahdollistaa nopeat UI-kokeilut.

**Toimenpiteet:**
1. Luo SvelteKit-projekti: `npm create svelte@latest my-app`
2. Asenna Supabase-client: `npm install @supabase/supabase-js`
3. Yhdistä Supabaseen (esim. lib/supabaseClient.js)
4. Rakenna päänäkymä:
    - **Datan haku**: RPC-funktio, joka hakee ja järjestää sisällöt kosini-samankaltaisuuden mukaan
    - **Scrollattava lista**: Svelten `#each`-lohko, moderni ja mobiiliystävällinen CSS
    - **Interaktiot**: "Tykkää" ja "Tallenna" -napit, jotka päivittävät Supabasen interactions-taulua
    - **Profiilin päivitys**: Edge Function, joka lähentää käyttäjän interest_vectoria tykätyn sisällön embeddingiin

> **Lopputulos:** Toimiva web-sovellus, jossa käyttäjä näkee ja personoi sisältöä reaaliajassa.

---

## Skaalautuvuus ja tuotantovalmius
- **Supabase** soveltuu hyvin tuotantoon, kunhan RLS-säännöt, varmuuskopiot ja monitorointi ovat kunnossa.
- **n8n** toimii hyvin automaatiossa, mutta jos prosessit monimutkaistuvat tai datamäärät kasvavat, voit siirtää workflowt koodiksi (esim. Python FastAPI, Node.js).
- **SvelteKit** on valmis tuotantoon ja skaalautuu hyvin.
- Kaikki osat ovat helposti laajennettavissa ja vaihdettavissa tarpeen mukaan.

---

## Kehityspolku MVP:stä tuotantoon
1. Aloita MVP:llä yllä kuvatulla pinolla.
2. Iteroi ja kerää käyttäjäpalautetta.
3. Siirrä kriittiset workflowt ja LLM-prosessointi koodiksi, jos skaalautuvuus tai räätälöitävyys sitä vaatii.
4. Lisää DevOps, logitus, testaus ja monitorointi tuotantovaiheessa.

---

**Yhteenveto:**
<<<<<<< HEAD
Tämä teknologiasuunnitelma mahdollistaa nopean kehityksen, testauksen ja skaalautuvuuden. Voit siirtyä MVP:stä tuotantoon vaiheittain ilman tarvetta uusia koko arkkitehtuuria.

---

## 7. Yksityiskohtaiset Tekniset Tehtävät (TODOista)

Nämä tehtävät on nostettu erillisestä `todo.md`-tiedostosta varmistamaan, että tekniset yksityiskohdat tulevat huomioiduiksi.

- **pgvector-tutkimus:** Perehdy syvällisesti Supabasen `pgvector`-laajennuksen toimintaan. Dokumentoi, miten vektoriupotusten tallennus, haku ja kosini-samankaltaisuuden laskenta toteutetaan käytännössä.
- **RLS-testaus:** Suunnittele ja toteuta kattavat testit Row Level Security (RLS) -politiikoille `profiles`- ja `interactions`-tauluissa. Varmista, että käyttäjä voi nähdä ja muokata ainoastaan omia tietojaan.
- **Testikäyttäjien luonti:** Lisää Supabase-projektiin useita testikäyttäjiä eri rooleilla (jos relevanttia) ja varmista, että käyttöoikeudet ja RLS-säännöt toimivat heidän osaltaan odotetusti.

---

## 8. Sisältölähteet (Datatekniikka)

Seuraavat datatekniikkaan keskittyvät lähteet tulee lisätä järjestelmään sisällönkeruun piiriin.

### 8.1. Blogit ja Verkkosivustot

- **Seattle Data Guy (Benjamin Rogojan):** https://www.theseattledataguy.com/
- **Start Data Engineering (Andreas Kretz):** https://www.startdataengineering.com/
- **Data Engineering Weekly:** https://www.dataengineeringweekly.com/
- **dbt Labs Blog:** https://www.getdbt.com/blog/
- **Confluent Blog (Apache Kafka):** https://www.confluent.io/blog/
- **Airbyte Blog:** https://airbyte.com/blog
- **Zach Wilson's Blog:** https://zachwilson.tech/

### 8.2. YouTube-kanavat

- **Seattle Data Guy:** https://www.youtube.com/@SeattleDataGuy
- **Start Data Engineering:** https://www.youtube.com/@StartDataEngineering
- **Thu Vu data analytics:** https://www.youtube.com/@ThuvuDataAnalytics

### 8.3. Yhteisöt

- **DataTalks.Club:** https://datatalks.club/
- **r/dataengineering (Reddit):** https://www.reddit.com/r/dataengineering/
- **Locally Optimistic:** https://locallyoptimistic.com/

### 8.4. Podcastit

- **The Data Engineering Podcast**
- **Data Engineering Show**
- **Monday Morning Data Chat**
- **The Analytics Engineering Podcast (dbt Labs)**
=======
Tämä teknologiasuunnitelma mahdollistaa nopean kehityksen, testauksen ja skaalautuvuuden. Voit siirtyä MVP:stä tuotantoon vaiheittain ilman tarvetta uusia koko arkkitehtuuria.
>>>>>>> 0135ef6e1f7344876442e2f8565de0df9f07ddd0
