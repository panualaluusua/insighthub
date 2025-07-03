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
- Dokumentointi ja näkyvä kehityshistoria auttavat sekä omaa että muiden ymmärrystä projektista.
- **YouTube-transkription optimointi:** OpenAI Whisper API:n ja FFmpeg-esikäsittelyn integrointi parantaa merkittävästi transkription laatua, nopeutta ja kustannustehokkuutta. Tämä osoittaa ulkoisten API-palveluiden ja tehokkaiden esikäsittelytyökalujen hyödyntämisen tärkeyden.

<<<<<<< HEAD
=======
---

Tämä tiedosto kokoaa keskeiset opit InsightHub-projektin toteutuksesta, ja toimii muistilistana tuleviin projekteihin.

>>>>>>> 0135ef6e1f7344876442e2f8565de0df9f07ddd0
## 8. Supabase ja MCP: opit ja käytännöt
- **Supabase** valittiin projektin tietokantapalveluksi, koska se tarjoaa PostgreSQL:n, autentikaation, REST/GraphQL-rajapinnat ja vektorituen (pgvector) helposti yhdestä paikasta.
- Supabasen käyttöönotto on nopeaa ja kehitys sujuu ilman raskasta infraa. Taulujen ja skeeman hallinta onnistuu sekä web-käyttöliittymästä että CLI:llä/migraatioilla.
- **MCP (Model Context Protocol)** mahdollistaa AI-avustajien (esim. Windsurf, Cursor, Claude) yhdistämisen suoraan Supabase-projektiin. AI-avustaja näkee skeeman ja voi ehdottaa SQL-migraatioita, kyselyitä ja tietomallin muutoksia suoraan kehitysympäristössä.
- MCP:n käyttöönotto vaatii Personal Access Tokenin luomisen Supabasessa ja yhteyden lisäämisen AI-työkalun asetuksiin.
- Yhdessä Supabase ja MCP nopeuttavat kehitystä, vähentävät virheitä ja mahdollistavat tuottavamman AI-avusteisen ohjelmistokehityksen.
<<<<<<< HEAD

## 9. Taskmaster, LLM API -käyttö, Memory Bank ja MCP
- **Taskmaster** on tehokas tehtävienhallintatyökalu, joka mahdollistaa projektin pilkkomisen pieniin, hallittaviin osiin (tasks, subtasks) ja seuraa etenemistä sekä riippuvuuksia.
    - Taskmasterin tag-järjestelmä mahdollistaa rinnakkaiset kehityshaara- ja ominaisuustyöt ilman konfliktia master-listan kanssa.
    - Tehtävien laatu paranee, kun käytetään analyysi- ja expand-työkaluja monimutkaisten kokonaisuuksien pilkkomiseen.
    - Iteratiivinen työskentely: suunnittele, jaa osiin, toteuta, reflektoi ja dokumentoi opit.
- **LLM API -käyttö** (esim. OpenAI, Claude, Perplexity) mahdollistaa automaattisen tehtävien generoinnin, koodin analyysin ja ajantasaisen tutkimuksen suoraan kehitystyön yhteydessä.
    - LLM-rajapintojen käyttö vaatii API-avainten hallintaa ja ympäristömuuttujien suojaamista.
    - LLM:tä kannattaa käyttää erityisesti tutkimukseen, best practices -hakuun ja monimutkaisten tehtävien pilkkomiseen.
- **Memory Bank** toimii projektin kollektiivisena muistina: kaikki tärkeät päätökset, opit, suunnitelmat ja reflektoinnit tallennetaan helposti löydettäviin markdown-tiedostoihin.
    - Memory Bankin ja Taskmasterin yhdistäminen mahdollistaa sekä "mitä tehdään" (Taskmaster) että "miksi ja miten" (Memory Bank) -tiedon hallinnan.
    - Reflektioiden ja learnings-tiedostojen päivittäminen auttaa välttämään samat virheet ja nopeuttaa uusien ominaisuuksien kehitystä.
- **MCP (Model Context Protocol)** mahdollistaa AI-avustajien syvemmän integraation projektin kontekstiin (esim. koodipuu, skeema, tehtävät), jolloin AI voi ehdottaa relevantteja muutoksia ja ratkaisuja suoraan projektin rakenteen pohjalta.
    - MCP:n avulla voidaan automatisoida sekä koodin generointi että tehtävienhallinta, mikä nopeuttaa kehitystä ja vähentää manuaalista työtä.
    - MCP:n käyttöönotto vaatii oikeat API-avaimet ja konfiguraation, mutta hyöty on merkittävä etenkin laajoissa projekteissa.

## 10. Uusi opittu workflow Taskmasterin workflow-säännöstä
- **Peruskehityssykli:**
    1. Listaa tehtävät (`list`).
    2. Valitse seuraava tehtävä (`next`).
    3. Tutki tehtävän yksityiskohdat (`show <id>`).
    4. Pilko monimutkaiset tehtävät pienempiin osiin (`expand <id>`).
    5. Toteuta: aloita testillä (TDD), kirjoita koodi, refaktoroi tarvittaessa.
    6. Kirjaa eteneminen ja löydökset (`update-subtask`).
    7. Merkitse tehtävät valmiiksi (`set-status`).
    8. Toista sykli.
- **Tagien käyttö:**
    - Oletuksena työskennellään master-tagissa, mutta rinnakkaiset kehityshaarat, tiimityö, kokeilut ja suuret ominaisuudet kannattaa eriyttää omiin tageihin.
    - Tagit mahdollistavat tehtävien eristämisen ja konfliktien välttämisen.
- **PRD-vetoinen kehitys:**
    - Suurille ominaisuuksille luodaan oma tagi ja Product Requirements Document (PRD), jonka perusteella generoituvat tehtävät.
    - PRD:n pohjalta analysoidaan monimutkaisuus ja pilkotaan tehtävät automaattisesti.
- **Memory Bank -integraatio:**
    - Taskmaster hallinnoi "mitä tehdään" (tehtävät), Memory Bank "miksi ja miten" (konteksti, päätökset, opit).
    - Reflektio ja oppien kirjaaminen Memory Bankiin auttaa kehityksen jatkuvassa parantamisessa.
- **Iteratiivinen ja joustava kehitys:**
    - Workflow mahdollistaa nopean prototypoinnin, jatkuvan parantamisen ja oppimisen.
    - Kehityssykliä ja workflowta päivitetään projektin edetessä ja tarpeiden muuttuessa.

## 11. n8n:n käyttö automaatiossa
- **n8n** on monipuolinen automaatioalusta, jonka avulla voi yhdistää eri palveluita ja automatisoida työnkulkuja ilman raskasta koodausta.
    - n8n:n visuaalinen editori tekee workflowjen rakentamisesta ja testaamisesta nopeaa ja intuitiivista.
    - Workflow-esimerkit (Reddit AI Digest, YouTube Summarizer, Podcast Summarizer) auttavat ymmärtämään parhaita käytäntöjä ja nopeuttavat kehitystä.
- **API-avainten ja autentikoinnin hallinta** on tärkeää: n8n:n omat API-avaimet ja ulkoisten palveluiden (Reddit, YouTube) avaimet tulee säilyttää turvallisesti ja konfiguroida oikein.
- **Ohjelmallinen workflow-import** onnistuu n8n:n REST API:n kautta, mutta yhteensopivuusongelmat ja autentikointivirheet ovat yleisiä. Usein helpointa on tuoda workflowt manuaalisesti UI:n kautta ja käyttää ohjelmallista tuontia vain yksinkertaisissa tapauksissa.
- **Parhaat käytännöt:**
    - Tallenna esimerkkityönkulut versionhallintaan (esim. workflow_examples/ -kansio).
    - Dokumentoi workflowjen tarkoitus ja käyttötapaukset.
    - Testaa workflowt huolellisesti sekä UI:ssa että ohjelmallisesti.
- **Haasteet ja ratkaisut:**
    - API-rajapintojen muutokset ja workflowjen yhteensopivuus voivat aiheuttaa ongelmia – seuraa n8n:n ja palveluiden dokumentaatiota.
    - Debuggaus onnistuu parhaiten n8n:n UI:ssa, jossa näkee jokaisen vaiheen tulokset visuaalisesti.
- **Yhteenveto:**
    - n8n nopeuttaa automaatioiden rakentamista ja mahdollistaa monimutkaisten työnkulkujen toteutuksen ilman syvää ohjelmointiosaamista.
    - Workflow-esimerkkien kerääminen ja analysointi auttaa rakentamaan InsightHubiin tehokkaita automaatioita.

---

Tämä tiedosto kokoaa keskeiset opit InsightHub-projektin toteutuksesta, ja toimii muistilistana tuleviin projekteihin.
=======
>>>>>>> 0135ef6e1f7344876442e2f8565de0df9f07ddd0
