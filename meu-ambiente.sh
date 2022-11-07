#!/usr/bin/zsh -xv

# Variáveis globais

declare -A var_dysconta

obtem_nome_sobrenome(){
  unset 'NOME'
  unset 'SOBRENOME'

  nome_completo=($(getent passwd "${USER}" | cut -d: -f5 | cut -d, -f1))
  NOME="${nome_completo[1]}"
  sobrenomes=${nome_completo[2,-1]}

  preposicoes=(de da das "do" dos e)
  sobrenomes_sem_preps=${sobrenomes}

  for prep in "${preposicoes[@]}"; do
      sobrenomes_sem_preps="${sobrenomes_sem_preps// ${prep} / }"
  done

  palavras=(${sobrenomes_sem_preps})
  num_palavras=${#palavras[@]}

  PS3="Olá, ${prim_nome}!
Por gentileza, informe o número de seu sobrenome preferido: "

  if [[ ${#palavras} -eq 1 ]]; then
    SOBRENOME="${palavras[1]}"
  elif [[ ${#palavras} -eq 0 ]]; then
    exit
  else
    select SOBRENOME in "${palavras[@]}"; do

        if [[ "${REPLY}" -gt 0 ]] && [[ "${REPLY}" -le "${#palavras}" ]]; then
          break
        fi
    done
  fi

  if ! [ -v APELIDO ]; then
    print "Olá, ${NOME}! Como você gostaria de ser chamado?"
    read APELIDO
    var_dysconta['APELIDO']="${APELIDO}"
  fi

  var_dysconta[NOME]="${NOME}"
  var_dysconta[SOBRENOME]="${SOBRENOME}"
}


principal(){
  # Carrega variáveis do zsh
  AMBIENTE="${HOME}/.zshenv"
  [ -f "${AMBIENTE}" ] && source "${AMBIENTE}"
  
  ! [ -v NOME ] || ! [ -v SOBRENOME ] && obtem_nome_sobrenome
  
  var_desejadas=(
    DISCIPLINA
    LAB
    PC
  )

  for v in "${var_desejadas[@]}"; do
    if ! [ -v "${v}" ]; then
      print -n "Por gentileza, defina um valor para ${v}: "
      read novo_valor

      var_dysconta[${v}]=${novo_valor}
    fi
  done

  # Reserva o animal para o usuário
  
  DISCIPLINA_DIR="/var/lib/dysconta/${DISCIPLINA}/animal"
  mkdir -p "${DISCIPLINA_DIR}"
  cd "${DISCIPLINA_DIR}"

  touch "${ANIMAL}" 2> /dev/null
  while [[ ! -O "${ANIMAL}" ]]; do
    print -n "Por gentileza, defina um valor para ANIMAL: "
    read ANIMAL
    print "${USER}" 1> "${ANIMAL}" 2> /dev/null
  done

  touch "${AMBIENTE}"
  for chave in ${(k)var_dysconta}
    if ! grep -E "^${chave}=" "${AMBIENTE}"; then
      echo ${chave}=${var_dysconta[$chave]} >> "${AMBIENTE}"
    else
      sed -i -e "s/^${chave}=.*/${chave}=${var_dysconta[$chave]}/" "${AMBIENTE}"
    fi

}

principal