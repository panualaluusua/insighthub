# Tehtävä #46: End-to-End Datamallien Yhtenäistäminen - Edistymisraportti

**Päiväys:** 2025-07-03
**Tehtävä:** #46: [Gemini] End-to-End Datamallien yhtenäistäminen (Pydantic & TypeScript)
**Tila:** Estetty (Blocked)

## 1. Tehtävän Tavoite

Tehtävän tavoitteena on yhtenäistää InsightHub-projektin back- ja frontendin datamallit. Tämä tarkoittaa Pydantic-mallien (backend) ja TypeScript-tyyppien (frontend) synkronointia niin, että ne edustavat samaa totuutta. Tavoitteena on parantaa tyyppiturvallisuutta, vähentää virheitä ja helpottaa kehitystä.

## 2. Tehdyt Toimenpiteet

1.  **Nykyisen tilanteen kartoitus:**
    *   Analysoitu Pydantic-mallit tiedostoista `src/models/content_relevance.py` ja `src/models/user_profile.py`.
    *   Analysoitu frontendin olemassa olevat TypeScript-tyypit, erityisesti `insighthub-frontend/src/lib/types/index.ts` ja `insighthub-frontend/src/lib/database.types.ts`.
    *   Tunnistettu, että `database.types.ts` on Supabase-generoitu ja edustaa tietokannan skeemaa, kun taas Pydantic-mallit edustavat prosessoitua sovellusdataa.

2.  **TypeScript-generointiskriptin luominen:**
    *   Luotu Python-skripti `scripts/generate_ts_types.py`, jonka tarkoituksena on generoida TypeScript-rajapinnat Pydantic-malleista (`ContentRelevance`, `ArticleQuality`, `UserProfile`, `UserInterests`).
    *   Skripti luo `insighthub-frontend/src/lib/generated_types/`-kansion ja tallentaa generoidut tyypit sinne (`pydantic_models.ts`).

3.  **Generoitujen tyyppien integroinnin aloitus frontendissä:**
    *   Lisätty tuonti `pydantic_models.ts`-tiedostosta `insighthub-frontend/src/lib/types/index.ts`-tiedostoon.
    *   Päivitetty `ContentCardItem`-tyyppi `insighthub-frontend/src/lib/types/index.ts`-tiedostossa laajentamaan `ContentRelevance`-tyyppiä.
    *   Päivitetty `generateMockContent`-funktio `insighthub-frontend/src/lib/stores/feedStore.ts`-tiedostossa luomaan mock-dataa, joka sisältää `relevance_score` ja `explanation` -kentät.
    *   Päivitetty `loadContent` ja `loadMoreContent` -funktioiden Supabase-kyselyt `feedStore.ts`-tiedostossa hakemaan myös `relevance_score` ja `explanation` -kentät.

## 3. Nykyinen Estävä Ongelma (Blocking Issue)

Tehtävän eteneminen on estynyt backend-testien ajamisessa. `poetry run pytest` -komento epäonnistuu `ModuleNotFoundError: No module named 'src'` -virheellä, kun se yrittää kerätä testejä `scripts/`-kansiosta. Tämä johtuu siitä, että `scripts/`-kansiossa olevat ajoskriptit (`run_local_youtube_test.py`, `run_youtube_test.py`) eivät ole varsinaisia testejä, mutta pytest yrittää käsitellä niitä testeinä, ja ne eivät löydä `src`-moduulia.

**Tehdyt korjausyritykset:**
*   Siirretty ajoskriptit `scripts/`-kansioon juurihakemistosta.
*   Lisätty `scripts/`-kansio `pytest.ini`-tiedoston `norecursedirs`-listaan, jotta pytest jättää sen huomiotta testejä kerätessään. Tämä korjaus ei kuitenkaan ratkaissut ongelmaa, vaan virhe toistuu edelleen.

## 4. Jäljellä Olevat Vaiheet

1.  **Ratkaise `pytest` `ModuleNotFoundError`:** Ennen kuin datamallien yhtenäistämistä voidaan jatkaa turvallisesti, on ehdottoman tärkeää saada backend-testit ajettua onnistuneesti. Tämä vaatii syvempää vianmääritystä siihen, miksi `pytest` edelleen yrittää tuoda `src`-moduulia `scripts/`-kansiosta, vaikka se on lisätty `norecursedirs`-listaan.
2.  **Jatka generoitujen tyyppien käyttöönottoa frontendissä:** Kun backend-testit toimivat, jatketaan `pydantic_models.ts`-tiedoston tyyppien vaiheittaista käyttöönottoa frontendissä, korvaten manuaalisia tyyppimäärityksiä.
3.  **Perusteellinen testaus:** Jokaisen merkittävän muutoksen jälkeen ajetaan back- ja frontendin automaattiset testit (`poetry run pytest`, `npm run test`, `npm run test:e2e`).
4.  **Manuaalinen savutesti:** Suoritetaan manuaalinen savutesti sovelluksessa varmistaen, että kaikki perustoiminnot ovat kunnossa.
5.  **Raportin päivitys ja tehtävän päättäminen:** Päivitetään tämä raportti ja merkitään tehtävä valmiiksi, kun kaikki vaiheet on suoritettu onnistuneesti.

---