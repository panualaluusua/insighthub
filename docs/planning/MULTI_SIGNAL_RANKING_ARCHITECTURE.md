---
description: "Architectural plan for the multi-signal content ranking system. This document is in Finnish."
---

# InsightHub: Monisignaalisen Sisältörankkauksen Arkkitehtoninen Suunnitelma

## Yhteenveto
Tämä asiakirja esittää InsightHub-projektin monisignaalisen sisältörankkausjärjestelmän ydinarkkitehtuurin. Tavoitteena on ylittää perinteisen semanttisen haun rajoitteet luomalla hienostunut relevanssipisteytys, joka palvelee vaativaa "Super-Alex"-kohdeyleisöä. Tämä yleisö arvostaa analyyttistä syvyyttä, laadukasta sisältöä ja tuoretta tietoa.

## 1. Nykytila ja Haasteet

### 1.1. Semanttisen Haun Rajoitteet
Perinteinen semanttinen haku (`pgvector`:in kosinisamanlaisuus) on tehokas ensimmäisen tason suodatin, mutta se ei yksin riitä "Super-Alex"-käyttäjän tarpeisiin. Se ei ota huomioon:
-   **Sisällön tuoreutta:** Uusi ja ajankohtainen sisältö on usein arvokkaampaa.
-   **Käyttäjän aiempaa toimintaa:** Aiemmat tykkäykset, tallennukset ja ohitukset ovat vahvoja signaaleja.
-   **Sisällön todellista laatua:** Lyhyt, mutta syvällinen artikkeli voi olla arvokkaampi kuin pitkä ja pinnallinen.

### 1.2. Lineaarisen Pisteytyksen Haasteet
Yksinkertainen lineaarinen malli, jossa lasketaan yhteen eri signaalit, on altis epätasapainolle. Esimerkiksi erittäin tuore, mutta heikkolaatuinen artikkeli voisi saada korkeammat pisteet kuin vanhempi, mutta laadukas ja syvällinen analyysi.

### 1.3. Arkkitehtoninen Suositus InsightHubille
Projektille suositellaan virallisesti **epälineaarista, monivaiheista rankkausmallia**. Tämä malli yhdistää useita signaaleja ja varmistaa, että korkealaatuinen ja käyttäjälle relevantti sisältö nousee johdonmukaisesti esiin.

## 2. Ehdotettu Arkkitehtuuri: Monivaiheinen Pisteytys

Arkkitehtuuri perustuu kolmeen pääsignaaliin: Tuoreus ($S_{freshness}$), Laatu ($S_{quality}$) ja Käyttäjävuorovaikutus ($S_{interaction}$). Nämä yhdistetään lopulliseksi relevanssipisteeksi ($S_{relevance}$).

### 2.1. Signaali 1: Tuoreuspisteet ($S_{freshness}$)
Tuoreus mallinnetaan eksponentiaalisella hajoamisfunktiolla.

-   **Puoliintumisaika (`half_life_hours`):** Aika tunneissa, jossa sisällön tuoreuspisteet puolittuvat.
-   **Kaava:**
    \[ S_{freshness} = \exp\left(- \frac{\ln(2) \cdot \text{age_in_hours}}{\text{half_life_hours}}\right) \]

#### Esimerkki Python-toteutuksesta
```python
import math
from datetime import datetime, timedelta

def calculate_freshness_score(published_at: datetime, half_life_hours: int = 24) -> float:
    """
    Calculates the freshness score of a content item based on its age.
    The score decays exponentially, halving every `half_life_hours`.
    """
    age = datetime.utcnow() - published_at
    age_in_hours = age.total_seconds() / 3600
    
    if age_in_hours < 0:
        return 1.0  # Content from the future is considered maximally fresh

    decay_rate = math.log(2) / half_life_hours
    freshness_score = math.exp(-decay_rate * age_in_hours)
    
    return freshness_score
```

### 2.2. Signaali 2: Laatupisteet ($S_{quality}$)
Laatupisteet ovat keskeinen erottava tekijä. Ne tuotetaan LLM-pohjaisella analyysillä, joka arvioi sisältöä useiden kriteerien perusteella.

#### Tietomalli: `ArticleQuality`
Tämä Pydantic-malli määrittelee laadun rakenteen.
```python
from pydantic import BaseModel, Field
from typing import List

class ArticleQuality(BaseModel):
    """
    Represents the assessed quality of an article or content piece.
    """
    clarity: int = Field(..., description="Clarity and ease of understanding (1-10).")
    depth: int = Field(..., description="Depth and thoroughness of analysis (1-10).")
    novelty: int = Field(..., description="Originality of ideas and novelty of insights (1-10).")
    actionability: int = Field(..., description="Provides practical, actionable advice (1-10).")
    overall_quality_score: float = Field(..., description="Weighted average quality score (0-1).")
```

#### Laatupisteiden laskenta
Pisteet lasketaan painotettuna keskiarvona:
\[ S_{quality} = \frac{(W_{clarity} \cdot C) + (W_{depth} \cdot D) + (W_{novelty} \cdot N) + (W_{actionability} \cdot A)}{10 \cdot (W_{clarity} + W_{depth} + W_{novelty} + W_{actionability})} \]
*Missä C, D, N, A ovat LLM:n antamat pisteet (1-10).*

### 2.3. Signaali 3: Käyttäjävuorovaikutus ($S_{interaction}$)
Tämä signaali perustuu käyttäjän aiempaan toimintaan.

-   **Positiiviset signaalit:** `like`, `save`
-   **Negatiiviset signaalit:** `hide`

#### Tietomalli: `InteractionSignal`
```python
from pydantic import BaseModel
from typing import Optional

class InteractionSignal(BaseModel):
    """
    Represents the interaction signal for a user-content pair.
    """
    has_positive_interaction: bool
    has_negative_interaction: bool
```
Pisteet lasketaan vuorovaikutuksen perusteella:
-   `1.0`: Jos on positiivinen vuorovaikutus.
-   `-1.0`: Jos on negatiivinen vuorovaikutus.
-   `0.0`: Ei vuorovaikutusta.

## 3. Relevanssipisteiden Yhdistäminen ($S_{relevance}$)

Relevanssi ei ole pelkkä summa, vaan dynaaminen, epälineaarinen yhdistelmä.

\[ S_{relevance} = (S_{semantic} \cdot W_{semantic}) \cdot (1 + S_{freshness} \cdot W_{freshness}) \cdot (1 + S_{quality} \cdot W_{quality}) + (S_{interaction} \cdot W_{interaction}) \]

-   **$S_{semantic}$:** `pgvector`:in kosinisamanlaisuus (0-1).
-   **Painokertoimet (W):** Määrittävät kunkin signaalin tärkeyden. Esim. `W_quality` voi olla korkea, jotta laatu korostuu.

Tämä malli varmistaa, että:
-   Heikkolaatuinen sisältö ($S_{quality} \approx 0$) saa matalat pisteet, vaikka se olisi tuoretta.
-   Käyttäjän negatiivinen vuorovaikutus ($S_{interaction} = -1.0$) laskee pisteitä merkittävästi.
-   Korkea laatu ja tuoreus vahvistavat toisiaan.

## 4. Integraatio Järjestelmään ja Toteutus

### 4.1. Sijoittuminen Arkkitehtuuriin: `ContentScorer`-solmu
Tässä dokumentissa kuvattu rankkauslogiikka toteutetaan osana `ContentScorer`-solmua, joka on määritelty `ARCHITECTURE.md`- ja `backend/AI_PIPELINE.md`-dokumenteissa. Tämä solmu on osa laajempaa `LangGraph`-pohjaista orkestrointia.

- **Syöte:** `ContentScorer` vastaanottaa `ContentState`-objektin, joka sisältää raakasisällön ja aiemmin lasketut embeddingit.
- **Toiminta:** Solmu suorittaa tämän dokumentin mukaisen monivaiheisen pisteytyksen.
- **Tuotos:** Solmu päivittää `ContentState`-objektin `relevance_score`-kentän.

### 4.2. Konfiguraation Keskittäminen (Best Practice)
Jotta rankkausalgoritmia voidaan helposti virittää ja A/B-testata ilman jatkuvia tietokantamuutoksia, on suositeltavaa, että kaikki painokertoimet ja maagiset luvut hallitaan keskitetysti Python-koodissa.

**Ehdotus:** Luodaan `RankingSettings`-dataclass `src/config.py`-tiedostoon:
```python
# src/config.py
from dataclasses import dataclass

@dataclass
class RankingSettings:
    W_SEMANTIC: float = 0.5
    W_FRESHNESS: float = 0.3
    W_QUALITY: float = 1.5  # Korostetaan laatua
    W_INTERACTION: float = 2.0 # Vahva vaikutus vuorovaikutukselle
    HALF_LIFE_HOURS: int = 48
```
Tietokantafunktio `get_ranked_content_for_user` tulisi muokata hyväksymään nämä arvot parametreina.

### 4.3. Tietomallien välinen suhde: `ArticleQuality` vs. `ContentRelevance`
Olemassa oleva `ContentRelevance`-malli (`src/models/content_relevance.py`) on yksinkertaisempi malli yleisen relevanssin arviointiin. Tässä dokumentissa ehdotettu `ArticleQuality`-malli on sen **edistyneempi ja yksityiskohtaisempi erikoistapaus**.

**Selvennys:**
- `ContentRelevance`: Voidaan käyttää nopeaan, ensimmäisen tason suodatukseen.
- `ArticleQuality`: Käytetään syvällisempään laadun arviointiin ja se on keskeinen osa lopullista `S_quality`-pisteytystä. Jatkokehityksessä nämä kaksi voidaan yhdistää tai `ArticleQuality` voi periä `ContentRelevance`-mallin.

### 4.4. Tietokantafunktion Esimerkki
Tässä on esimerkki PostgreSQL-funktiosta, joka toteuttaa rankkauslogiikan.

```sql
CREATE OR REPLACE FUNCTION get_ranked_content_for_user(
    p_user_id UUID,
    p_user_interest_vector vector(1536),
    p_match_threshold FLOAT,
    p_match_count INT
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    url TEXT,
    published_at TIMESTAMPTZ,
    content_type TEXT,
    relevance_score FLOAT
) AS $$
DECLARE
    -- Painokertoimet (W) ja muut parametrit
    -- HUOM: Nämä tulisi siirtää Python-konfiguraatioon ja antaa parametreina
    W_SEMANTIC FLOAT := 0.5;
    W_FRESHNESS FLOAT := 0.3;
    W_QUALITY FLOAT := 1.5;
    W_INTERACTION FLOAT := 2.0;
    HALF_LIFE_HOURS INT := 48;
BEGIN
    RETURN QUERY
    WITH semantic_scores AS (
        -- Vaihe 1: Semanttinen haku
        SELECT
            c.id,
            c.title,
            c.url,
            c.published_at,
            c.content_type,
            (1 - (c.embedding <=> p_user_interest_vector)) AS semantic_score
        FROM
            content c
        WHERE (1 - (c.embedding <=> p_user_interest_vector)) > p_match_threshold
    ),
    interaction_scores AS (
        -- Vaihe 2: Käyttäjävuorovaikutus
        SELECT
            ss.id,
            COALESCE(
                MAX(CASE
                    WHEN i.interaction_type IN ('like', 'save') THEN 1.0
                    WHEN i.interaction_type = 'hide' THEN -1.0
                    ELSE 0.0
                END), 0.0
            ) AS interaction_score
        FROM
            semantic_scores ss
        LEFT JOIN
            interactions i ON ss.id = i.content_id AND i.user_id = p_user_id
        GROUP BY
            ss.id
    )
    -- Yhdistetään kaikki pisteet ja lasketaan lopullinen relevanssi
    SELECT
        ss.id,
        ss.title,
        ss.url,
        ss.published_at,
        ss.content_type,
        -- Lopullinen relevanssipisteiden laskenta
        (ss.semantic_score * W_SEMANTIC) *
        (1 + (exp(- (ln(2) * EXTRACT(EPOCH FROM (NOW() - ss.published_at)) / 3600) / HALF_LIFE_HOURS)) * W_FRESHNESS) *
        (1 + (cq.overall_quality_score * W_QUALITY)) +
        (inter.interaction_score * W_INTERACTION) AS final_relevance_score
    FROM
        semantic_scores ss
    JOIN
        content_quality cq ON ss.id = cq.content_id
    JOIN
        interaction_scores inter ON ss.id = inter.id
    ORDER BY
        final_relevance_score DESC
    LIMIT p_match_count;
END;
$$ LANGUAGE plpgsql;
```

## 5. Seuraavat Askeleet
1.  **Toteutus:** Toteutetaan yllä kuvattu logiikka `ContentScorer`-solmussa ja tietokantafunktiossa.
2.  **Testaus:** Testataan rankkausmallia laajasti erilaisilla sisällöillä ja käyttäjäprofiileilla.
3.  **Iterointi:** Kerätään dataa ja käyttäjäpalautetta mallin jatkuvaa virittämistä varten. LangSmith-integraatio on tässä avainasemassa.