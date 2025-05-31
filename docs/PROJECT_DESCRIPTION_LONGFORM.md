# InsightHub: Projektikuvaus (pitkä muoto)

Tämä sivu on tarkoitettu InsightHub-projektin teknisemmäksi ja perusteellisemmaksi esittelyksi. Se sopii julkaistavaksi esimerkiksi henkilökohtaisilla nettisivuillasi. Mukana on linkki esittelyvideoon sekä yksityiskohtainen kuvaus projektin taustoista, kehitysvaiheista ja teknisistä ratkaisuista.

---

## Esittelyvideo
Katso lyhyt video InsightHubin tarinasta ja käyttötavoista:

[Lisää tähän linkki videoon, kun se on julkaistu]

---

## Projektin tausta ja motivaatio
InsightHub syntyi tarpeesta hallita alati kasvavaa tekoäly- ja LLM-uutisvirtaa sekä kuratoida tietoa tehokkaasti. Kehittäjänä huomasin, että perinteiset tavat seurata alan kehitystä (uutiset, Reddit, YouTube, some) johtivat helposti ylikuormitukseen ja tiedon välttelyyn. Tavoitteena oli luoda työkalu, joka auttaa nopeasti hahmottamaan viikon tärkeimmät tapahtumat ja mahdollistaa syvemmän sukelluksen kiinnostaviin aiheisiin.

---

## Tekninen toteutus ja kehitysvaiheet

### 1. Reddit- ja YouTube-lähteiden keruu
Projektin ensimmäisessä vaiheessa toteutin Python-skriptin, joka hyödyntää Redditin API:a. Skripti hakee valituista subredditeistä viikon suosituimmat postaukset ja niiden url-osoitteet. Tämän jälkeen mukaan otettiin myös YouTube-kanavat, joiden tuoreimmat videot haetaan automaattisesti.

### 2. Lähteiden syöttö ja automaatio
Alkuvaiheessa lähteiden syöttö Google Notebook LM -sovellukseen automatisoitiin Seleniumilla. Prosessi osoittautui kuitenkin hitaaksi ja virheherkäksi, joten ratkaisuksi löytyi Chrome-lisäosa, johon voi syöttää url-listan ja joka lisää lähteet Notebook LM:ään kerralla.

### 3. Podcast-muotoiset tiivistelmät
InsightHubin ytimessä on kyky muuntaa kerätty tieto helposti kuunneltavaan muotoon. NotebookLM:n "Audio Overview" -ominaisuutta personoitiin ohjaavilla kehotteilla (promptit), esimerkiksi kolmiosaisella rakenteella: määritelmä, sovellukset ja tulevaisuus. Tämä toi podcast-koosteisiin vaihtelua ja syvyyttä.

#### Esimerkkikehote:
> Break the podcast into three parts: [Part 1 definition], [Part 2 applications], [Part 3 future]

---

## Käytetyt teknologiat
- Python (Reddit API, YouTube API, Selenium)
- Streamlit (käyttöliittymä)
- Google Notebook LM (tiedon tiivistys ja audio)
- Chrome-lisäosa lähteiden syöttöön

---

## Oppimiskokemukset ja jatkokehitys
Projektin aikana opin paljon tiedonkeruun automaatiosta, API-rajapinnoista ja tekoälytyökalujen personoinnista. InsightHubia kehitetään edelleen käyttäjäpalautteen pohjalta – tavoitteena on tuoda mukaan lisää lähteitä, parantaa tiivistysten laatua ja mahdollistaa entistä joustavampi tiedonhallinta.

---

## Ota yhteyttä tai kokeile itse
[Lisää tähän yhteystiedot, linkki InsightHubin demo-/projektisivulle, GitHub-repo jne.]

---

*Päivitetty: [päivämäärä]*
