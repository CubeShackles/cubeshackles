[English](INSTITUTIONAL_README_PATTERN.md) | [Português](INSTITUTIONAL_README_PATTERN.pt.md)

# Padrão de README Institucional

**Proprietário: CubeShackles (liderado pelo fundador).**

Um padrão de documentação mais rigoroso para repositórios onde a linguagem
institucional mais importa — infraestrutura de mercado financeiro e
superfícies de integração institucional (Lote 2 em diante). Complementa,
sem substituir, o
[`REPOSITORY_README_TEMPLATE.md`](REPOSITORY_README_TEMPLATE.md): use o
bloco de propriedade, o campo Estado do bloco de propriedade e a linguagem
geral de doutrina da plataforma desse modelo, e estruture depois o corpo do
README de um repositório institucional em torno das doze secções abaixo.

Introduzido com o Lote 2 (2026-07-19). Aplicado inicialmente a:
`cubeshackles-ledger`, `cubeshackles-clearing-house`,
`cubeshackles-settlement-engine`, `cubeshackles-institutional-gateway`,
`cubeshackles-regulatory-reporting`, `cubeshackles-contracts`.

## As doze secções

1. **Finalidade** — o que o repositório faz, um parágrafo.
2. **Papel na CubeShackles** — a sua posição na cadeia de controlo de
   finanças institucionais (ver `cubeshackles/REPOSITORY_MAP.md` §8); o que
   o alimenta, o que ele alimenta.
3. **Âmbito**
4. **Fora do âmbito** — explícito, não implícito.
5. **Arquitetura funcional** — componentes, não detalhe de implementação.
6. **Fronteira de confiança** — o que atravessa a fronteira, o que é
   assumido versus verificado.
7. **Fluxo de dados** — transições de estado ou fluxo de mensagens, se
   aplicável.
8. **Modelo de segurança** — específico do repositório; ligar a
   `SECURITY_MODEL.md` para o modelo de toda a plataforma em vez de o
   repetir.
9. **Considerações regulatórias** — ver abaixo; esta é a secção com maior
   probabilidade de necessitar de entradas no Registo de Reivindicações.
10. **Estado de implementação atual** — ver a convenção de etiquetas de
    Estado abaixo.
11. **Roteiro** — claramente identificado como roteiro, nunca reafirmado
    como estado atual.
12. **Referências de documentação**

Omitir uma secção apenas quando genuinamente não aplicável (por exemplo, um
repositório de autoridade de esquema sem fluxo de dados ao vivo) —
declarando-o explicitamente em vez de eliminar o cabeçalho silenciosamente,
para que a paridade de cabeçalhos entre inglês e português se mantenha
intacta e a omissão seja visível, não silenciosa.

## Etiquetas de maturidade: `**Status:**` / `**Estado:**`

Cada afirmação sobre o que o repositório atualmente faz — mais
frequentemente dentro de "Arquitetura funcional," "Fronteira de confiança,"
"Fluxo de dados," e "Estado de implementação atual" — deve ser etiquetada
em linha com um dos seis termos de maturidade controlados:

| English | Português |
|---|---|
| `**Status:** Implemented` | `**Estado:** Implementado` |
| `**Status:** Partially implemented` | `**Estado:** Parcialmente implementado` |
| `**Status:** Prototype` | `**Estado:** Protótipo` |
| `**Status:** Experimental` | `**Estado:** Experimental` |
| `**Status:** Planned` | `**Estado:** Planeado` |
| `**Status:** Proposed` | `**Estado:** Proposto` |

O `scripts/validate_localization.py` aplica isto: as sequências de etiquetas
em inglês e português devem corresponder 1 a 1 através da tabela acima. Uma
tradução não pode suavizar "Prototype" para "Implementado," nem omitir uma
etiqueta apenas de um dos lados. Este é um subconjunto mais restrito do
vocabulário de maturidade completo em
[`LOCALIZATION_POLICY.md`](LOCALIZATION_POLICY.md) §4 (que também cobre o
campo `Estado` do bloco de propriedade, referente ao repositório como um
todo) — os seis termos acima destinam-se especificamente a etiquetar a
maturidade de uma capacidade em linha, não do repositório inteiro.

## Aplicação do Registo de Reivindicações

O `scripts/validate_localization.py` também aplica isto (Regra 1,
adicionada em 2026-07-19): qualquer parágrafo em `README.md` que utilize um
termo institucional sensível — regulador, banco central, liquidação,
compensação, custódia, tokenização, supervisão, conformidade, auditoria,
soberano — deve pertencer a um repositório já listado em
[`CLAIMS_REGISTER.md`](CLAIMS_REGISTER.md), ou conter um qualificador em
linha (uma etiqueta `**Status:**`/`**Estado:**`, ou expressões como
"planeado," "protótipo," "sandbox," "não representa," "não existe," etc.)
que marque a afirmação como delimitada em vez de uma reivindicação ao vivo.
Cada repositório do Lote 2 recebe pelo menos uma entrada no Registo de
Reivindicações como parte da sua documentação — normalmente o caminho mais
simples.

**Lacuna conhecida, registada, não silenciada:** esta regra ainda não é
aplicada retroativamente a `cubeshackles`, `cubeshackles-developer-portal`
ou `.github` — a sua prosa existente utiliza legitimamente este vocabulário
como descrição arquitetural da plataforma, mas é anterior à regra e não tem
entrada no registo. Nenhum CI de repositório invoca atualmente o validador
(`docs-localization.yml` ainda não tem workflow chamador em lado nenhum),
pelo que isto não é uma quebra de CI ao vivo — é uma lacuna documentada para
um futuro lote de correção. Ver `LOCALIZATION_ROLLOUT.md`.

## Linguagem ambígua — disciplina de autoria, ainda não uma regra do validador

Evitar o uso não qualificado de: **regulator-grade**, **institutional-grade**,
**production-ready** (já um termo absolutamente proibido, ver
`DOCUMENTATION_STANDARD.md` §3), **sovereign infrastructure** — a menos que
a afirmação seja precisamente qualificada na mesma frase (o que
especificamente é "regulator-grade," e que evidência o sustenta). Esta é
atualmente uma regra de autoria para o Lote 2, não uma verificação
bloqueante do validador: "regulator-grade" e "sovereign infrastructure" já
aparecem sem qualificação no README guarda-chuva `cubeshackles` já
integrado, como parte da sua linguagem de posicionamento aprovada pelo
fundador, anterior a este padrão. Transformar isto numa regra rígida do
validador exigiria primeiro uma correção desse conteúdo — registado, não
feito aqui.

<!--
localization:
  canonical_file: INSTITUTIONAL_README_PATTERN.md
  locale: pt-AO
  translation_status: machine-assisted
  canonical_commit: 6609902376b448bdca3e457392941a07947015a4
  last_synchronized: 2026-07-19
-->
