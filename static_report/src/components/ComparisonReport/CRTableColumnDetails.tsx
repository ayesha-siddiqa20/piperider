import { Code, Flex, Text } from '@chakra-ui/react';
import { ColumnSchema } from '../../sdlc/single-report-schema';
import { ZColSchema, zReport } from '../../types';
import { GeneralTableColumn } from '../shared/GeneralTableColumn';
import { MetricsInfo } from '../shared/MetricsInfo';
import { NumericTableColumn } from '../shared/NumericTableColumn';

// props made optional as they can be undefined
type CRTableColumnDetailsProps = {
  baseColumn?: ColumnSchema | undefined;
  targetColumn?: ColumnSchema | undefined;
};
export const CRTableColumnDetails = ({
  baseColumn,
  targetColumn,
}: CRTableColumnDetailsProps) => {
  const emptyLabel = '-';
  const fallback = baseColumn || targetColumn;
  zReport(ZColSchema.safeParse(baseColumn));
  zReport(ZColSchema.safeParse(targetColumn));

  return (
    <Flex direction="column" gap={2} minH="250px">
      <Flex direction="column" gap={3}>
        <Flex justifyContent="space-between">
          <Text maxWidth="calc(100% - 250px)">
            <Text
              as="span"
              fontWeight={700}
              color="gray.900"
              fontSize="lg"
              mr={1}
              noOfLines={1}
              title={fallback.name}
            >
              {fallback.name}
            </Text>
            {''}(<Code>{fallback.schema_type}</Code>)
          </Text>

          <Flex gap={8}>
            <Text fontWeight={700} textAlign="right" width="100px">
              Base
            </Text>
            <Text fontWeight={700} textAlign="right" width="100px">
              Target
            </Text>
          </Flex>
        </Flex>

        <Flex direction="column" mt={3}>
          {/* Case: Cast provided undefined to null */}
          <GeneralTableColumn
            targetColumn={targetColumn || null}
            baseColumn={baseColumn}
          />
        </Flex>
        {fallback.type === 'numeric' && (
          <>
            <NumericTableColumn
              baseColumn={baseColumn}
              targetColumn={targetColumn}
            />
          </>
        )}

        {fallback.type === 'datetime' && (
          <Flex direction="column">
            <MetricsInfo
              name="Min"
              firstSlot={baseColumn?.min ?? emptyLabel}
              secondSlot={targetColumn?.min ?? emptyLabel}
            />
            <MetricsInfo
              name="Max"
              firstSlot={baseColumn?.max ?? emptyLabel}
              secondSlot={targetColumn?.max ?? emptyLabel}
            />
          </Flex>
        )}
      </Flex>
    </Flex>
  );
};
